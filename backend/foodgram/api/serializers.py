import base64
import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredientsRelated,
)
from rest_framework import serializers
from users.models import Subscription

User = get_user_model()

# Константы валидации
AMOUNT_MIN = 1
AMOUNT_MAX = 32000
COOKING_TIME_MIN = 1
COOKING_TIME_MAX = 32000


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f"{uuid.uuid4()}.{ext}")
        return super().to_internal_value(data)


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            request.user.subscriptions.filter(author=obj).exists()
        return False


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ("id", "email", "username", "first_name", "last_name", "password")
        extra_kwargs = {"password": {"write_only": True}}


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


# --- INGREDIENTS: READ vs WRITE ---


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(source="ingredient.measurement_unit")
    amount = serializers.ReadOnlyField()

    class Meta:
        model = RecipeIngredientsRelated
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeIngredientWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=AMOUNT_MIN, max_value=AMOUNT_MAX)


# --- MAIN RECIPE SERIALIZERS ---


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientReadSerializer(many=True, source="recipe_ingredients")
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "name",
            "image",
            "text",
            "cooking_time",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return request.user.favorites.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return request.user.shopping_cart.filter(recipe=obj).exists()
        return False


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientWriteSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "text", "cooking_time", "ingredients")

    def validate_cooking_time(self, value):
        if not COOKING_TIME_MIN <= value <= COOKING_TIME_MAX:
            raise serializers.ValidationError(
                f"Время приготовления должно быть от {COOKING_TIME_MIN} до {COOKING_TIME_MAX} минут."
            )
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError("Добавьте хотя бы один ингредиент.")
        ingredients_ids = [item["id"] for item in value]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError("Ингредиенты не должны повторяться.")

        # Проверка существования ингредиентов
        existing_ids = set(
            Ingredient.objects.filter(id__in=ingredients_ids).values_list(
                "id", flat=True
            )
        )

        if len(existing_ids) != len(ingredients_ids):
            missing_ids = set(ingredients_ids) - existing_ids
            raise serializers.ValidationError(
                f"Ингредиенты с id {missing_ids} не существуют."
            )

        return value

    def create_ingredients(self, ingredients_data, recipe):
        objs = []
        for item in ingredients_data:
            try:
                ingredient = Ingredient.objects.get(id=item["id"])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    f'Ингредиент с id={item["id"]} не найден.'
                )
            objs.append(
                RecipeIngredientsRelated(
                    recipe=recipe, ingredient=ingredient, amount=item["amount"]
                )
            )
        RecipeIngredientsRelated.objects.bulk_create(objs)

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        validated_data.pop("author", None)

        recipe = Recipe.objects.create(
            author=self.context["request"].user, **validated_data
        )
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients", None)

        if ingredients_data is None:
            raise serializers.ValidationError(
                {"ingredients": "Поле ingredients обязательно при обновлении."}
            )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        RecipeIngredientsRelated.objects.filter(recipe=instance).delete()
        self.create_ingredients(ingredients_data, instance)

        return instance


# --- SUBSCRIPTIONS ---


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="author.email")
    username = serializers.CharField(source="author.username")
    first_name = serializers.CharField(source="author.first_name")
    last_name = serializers.CharField(source="author.last_name")
    id = serializers.IntegerField(source="author.id")
    avatar = serializers.ImageField(source="author.avatar", read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "avatar",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        return True

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes_limit = request.query_params.get("recipes_limit")
        recipes = obj.author.recipes.all()

        if recipes_limit is not None and recipes_limit.isdigit():
            recipes = recipes[: int(recipes_limit)]

        return RecipeShortSerializer(recipes, many=True, context=self.context).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()
