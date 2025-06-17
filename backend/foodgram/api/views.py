from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Ingredient, Recipe, RecipeIngredientsRelated, ShoppingList
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription

from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CustomUserCreateSerializer,
    CustomUserSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeShortSerializer,
    RecipeWriteSerializer,
    SubscriptionSerializer,
)

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["author"]
    search_fields = ["ingredients__name"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        read_serializer = RecipeSerializer(
            serializer.instance, context=self.get_serializer_context()
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        read_serializer = RecipeSerializer(
            serializer.instance, context=self.get_serializer_context()
        )
        return Response(read_serializer.data)

    def get_queryset(self):
        queryset = Recipe.objects.select_related("author").prefetch_related(
            "recipe_ingredients__ingredient"
        )
        user = self.request.user
        is_favorited = self.request.query_params.get("is_favorited")
        is_in_shopping_cart = self.request.query_params.get("is_in_shopping_cart")

        if user.is_authenticated:
            if is_favorited == "1":
                queryset = queryset.filter(favorited_by__user=user)
            if is_in_shopping_cart == "1":
                queryset = queryset.filter(in_shopping_carts__user=user)

        return queryset

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return RecipeWriteSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == "POST":
            obj, created = request.user.favorites.get_or_create(recipe=recipe)
            if not created:
                return Response(
                    {"errors": "Рецепт уже в избранном"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Вернуть краткий рецепт в ответе
            serializer = RecipeShortSerializer(recipe, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # DELETE-запрос
        deleted, _ = request.user.favorites.filter(recipe=recipe).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"errors": "Рецепт не найден в избранном"},
            status=HTTPStatus.BAD_REQUEST,
        )

    @action(
        detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == "POST":
            obj, created = ShoppingList.objects.get_or_create(
                user=request.user, recipe=recipe
            )
            if not created:
                return Response(
                    {"errors": "Рецепт уже в списке покупок"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Возвращаем сериализованный рецепт в формате короткого описания
            from .serializers import RecipeShortSerializer

            serializer = RecipeShortSerializer(recipe, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # DELETE-запрос
        deleted, _ = request.user.shopping_cart.filter(recipe=recipe).delete()

        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "Рецепт не найден в списке покупок"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredientsRelated.objects.filter(
                recipe__in=ShoppingList.objects.filter(user=request.user).values_list(
                    "recipe_id", flat=True
                )
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total=Sum("amount"))
        )

        shopping_list = "Список покупок:\n\n"
        for item in ingredients:
            shopping_list += f"- {item['ingredient__name']} ({item['total']} {item['ingredient__measurement_unit']})\n"

        return HttpResponse(
            shopping_list,
            content_type="text/plain",
            headers={"Content-Disposition": 'attachment; filename="shopping_list.txt"'},
            status=200,
        )

    @action(
        detail=True, methods=["get"], url_path="get-link", permission_classes=[AllowAny]
    )
    def get_link(self, request, pk=None):
        try:
            recipe = self.get_object()
            short_link = request.build_absolute_uri(f"/recipes/{recipe.id}/")
            return Response({"short-link": short_link}, status=status.HTTP_200_OK)
        except Recipe.DoesNotExist:
            return Response(
                {"detail": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND
            )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    http_method_names = ["get", "post", "patch", "put", "delete"]

    def get_serializer_class(self):
        if self.action == "create":
            return CustomUserCreateSerializer
        return CustomUserSerializer

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        if self.action in ["list", "retrieve", "me"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(
        detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)

        if request.method == "POST":
            if author == request.user:
                return Response(
                    {"errors": "Нельзя подписаться на самого себя"},
                    status=HTTPStatus.BAD_REQUEST,
                )
            subscription, created = Subscription.objects.get_or_create(
                user=request.user, author=author
            )
            if not created:
                return Response(
                    {"errors": "Вы уже подписаны на этого пользователя"},
                    status=HTTPStatus.BAD_REQUEST,
                )

            serializer = SubscriptionSerializer(
                subscription, context={"request": request}
            )
            return Response(serializer.data, status=HTTPStatus.CREATED)

        deleted, _ = request.user.subscriptions.filter(author=author).delete()
        if deleted:
            return Response(status=HTTPStatus.NO_CONTENT)

        return Response(
            {"errors": "Вы не были подписаны на этого пользователя"},
            status=HTTPStatus.BAD_REQUEST,
        )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribers__user=request.user)

        page = self.paginate_queryset(queryset)
        subscriptions = request.user.subscriptions.select_related("author")
        subscription_map = {s.author_id: s for s in subscriptions}

        if page is not None:
            serializer = SubscriptionSerializer(
                [subscription_map[user.id] for user in page],
                many=True,
                context={"request": request},
            )
            return self.get_paginated_response(serializer.data)

        serializer = SubscriptionSerializer(
            [subscription_map[user.id] for user in queryset],
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def me(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Учетные данные не были предоставлены."},
                status=HTTPStatus.UNAUTHORIZED,
            )

        serializer = self.get_serializer(request.user, context={"request": request})
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="set_password",
        permission_classes=[IsAuthenticated],
    )
    def set_password(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not current_password or not new_password:
            return Response(
                {"detail": "Оба поля обязательны."}, status=HTTPStatus.BAD_REQUEST
            )

        if not user.check_password(current_password):
            return Response(
                {"current_password": ["Неверный пароль."]},
                status=HTTPStatus.BAD_REQUEST,
            )

        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            return Response(
                {"new_password": list(e.messages)}, status=HTTPStatus.BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        return Response(
            {"detail": "Пароль успешно изменён."}, status=HTTPStatus.NO_CONTENT
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset
