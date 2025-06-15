import csv
from io import BytesIO

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favourite, Ingredient, Recipe,
                            RecipeIngredientsRelated, ShoppingList)
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import Subscription

from .permissions import IsAuthorOrReadOnly
from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          IngredientSerializer, RecipeSerializer,
                          RecipeWriteSerializer, SubscriptionSerializer)

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
                queryset = queryset.filter(favorite__user=user)
            if is_in_shopping_cart == "1":
                queryset = queryset.filter(shoppinglist__user=user)

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
            obj, created = Favourite.objects.get_or_create(
                user=request.user, recipe=recipe
            )
            if not created:
                return Response(
                    {"errors": "Рецепт уже в избранном"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Вернуть краткий рецепт в ответе
            from .serializers import RecipeShortSerializer

            serializer = RecipeShortSerializer(recipe, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # DELETE-запрос
        deleted, _ = Favourite.objects.filter(user=request.user, recipe=recipe).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"errors": "Рецепт не найден в избранном"},
            status=status.HTTP_400_BAD_REQUEST,
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
        deleted, _ = ShoppingList.objects.filter(
            user=request.user, recipe=recipe
        ).delete()
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
                recipe__shoppinglist__user=request.user
            )
            .values("ingredient__name", "ingredient__measurement")
            .annotate(total=Sum("count"))
        )

        file_format = request.query_params.get("format", "txt")

        if file_format == "pdf":
            buffer = BytesIO()
            p = canvas.Canvas(buffer)
            p.setFont("Helvetica", 14)
            p.drawString(100, 800, "Список покупок:")

            y = 780
            for item in ingredients:
                line = f"- {item['ingredient__name']} ({item['total']} {item['ingredient__measurement']})"
                p.drawString(100, y, line)
                y -= 20
                if y < 50:
                    p.showPage()
                    p.setFont("Helvetica", 14)
                    y = 800

            p.showPage()
            p.save()

            buffer.seek(0)
            return HttpResponse(
                buffer,
                content_type="application/pdf",
                headers={
                    "Content-Disposition": 'attachment; filename="shopping_list.pdf"'
                },
            )

        # По умолчанию .txt
        shopping_list = "Список покупок:\n\n"
        for item in ingredients:
            shopping_list += f"- {item['ingredient__name']} ({item['total']} {item['ingredient__measurement']})\n"

        return HttpResponse(
            shopping_list,
            content_type="text/plain",
            headers={"Content-Disposition": 'attachment; filename="shopping_list.txt"'},
        )

    @action(
        detail=True, methods=["get"], url_path="get-link", permission_classes=[AllowAny]
    )
    def get_link(self, request, pk=None):
        try:
            recipe = self.get_object()
            short_link = f"https://example.com/recipes/{recipe.id}/"
            return Response({"short-link": short_link}, status=status.HTTP_200_OK)
        except Recipe.DoesNotExist:
            return Response(
                {"detail": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
        if self.action in ["list", "retrieve"]:
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
                    status=status.HTTP_400_BAD_REQUEST,
                )

            subscription, created = Subscription.objects.get_or_create(
                user=request.user, author=author
            )

            if not created:
                return Response(
                    {"errors": "Вы уже подписаны на этого пользователя"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = SubscriptionSerializer(
                subscription, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted, _ = Subscription.objects.filter(
            user=request.user, author=author
        ).delete()

        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"errors": "Вы не были подписаны на этого пользователя"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribers__user=request.user)

        page = self.paginate_queryset(queryset)
        subscriptions = Subscription.objects.filter(
            user=request.user, author__in=queryset
        )
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
                {
                    "id": None,
                    "email": None,
                    "username": None,
                    "first_name": None,
                    "last_name": None,
                    "is_subscribed": False,
                    "avatar": None,
                },
                status=status.HTTP_200_OK,
            )

        serializer = self.get_serializer(request.user, context={"request": request})
        return Response(serializer.data)

    @action(
        detail=False,  # Не привязано к конкретному пользователю (работает с текущим)
        methods=["post"],
        url_path="set_password",  # URL будет /users/set_password/
        permission_classes=[IsAuthenticated],  # Только для авторизованных
    )
    def set_password(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not current_password or not new_password:
            return Response({"detail": "Оба поля обязательны."}, status=400)

        if not user.check_password(current_password):
            return Response({"current_password": ["Неверный пароль."]}, status=400)

        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            return Response({"new_password": list(e.messages)}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({"detail": "Пароль успешно изменён."}, status=200)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
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
