from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from users.models import Subscription
from recipes.models import (
    Recipe, RecipeIngredientsRelated, Ingredient,
    ShoppingList, Favourite
)
import base64
import uuid

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr),
                name=f'{uuid.uuid4()}.{ext}'
            )
        return super().to_internal_value(data)

class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, author=obj).exists()
        return False


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.CharField(source='measurement', read_only=True)
    
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


# --- INGREDIENTS: READ vs WRITE ---

class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement')
    amount = serializers.ReadOnlyField(source='count')

    class Meta:
        model = RecipeIngredientsRelated
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    count = serializers.IntegerField()

    def validate_count(self, value):
        if value <= 0:
            raise serializers.ValidationError('Количество должно быть больше нуля.')
        return value

    def to_internal_value(self, data):
        data = data.copy()
        if 'amount' in data:
            data['count'] = data.pop('amount')
        return super().to_internal_value(data)


# --- MAIN RECIPE SERIALIZERS ---

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientReadSerializer(
        many=True, source='recipe_ingredients'
    )
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'text',
            'cooking_time', 'ingredients',
            'is_favorited', 'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favourite.objects.filter(user=request.user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingList.objects.filter(user=request.user, recipe=obj).exists()
        return False


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientWriteSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'text', 'cooking_time',
            'ingredients'
        )

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError('Добавьте хотя бы один ингредиент.')
        ingredients_ids = [item['id'] for item in value]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError('Ингредиенты не должны повторяться.')
        return value

    def create_ingredients(self, ingredients_data, recipe):
        objs = []
        for item in ingredients_data:
            try:
                ingredient = Ingredient.objects.get(id=item['id'])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    f'Ингредиент с id={item["id"]} не найден.'
                )
            objs.append(RecipeIngredientsRelated(
                recipe=recipe,
                ingredient=ingredient,
                count=item['count']
            ))
        RecipeIngredientsRelated.objects.bulk_create(objs)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        validated_data.pop('author', None)

        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.get('ingredients')

        if ingredients_data is None:
            raise serializers.ValidationError({
                'ingredients': 'Поле ingredients обязательно при обновлении.'
            })

        validated_data.pop('ingredients')  # удалим после проверки

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        RecipeIngredientsRelated.objects.filter(recipe=instance).delete()
        self.create_ingredients(ingredients_data, instance)

        return instance


# --- SUBSCRIPTIONS ---

class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='author.email')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    id = serializers.IntegerField(source='author.id')
    avatar = serializers.ImageField(source='author.avatar', read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'avatar', 'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return True  # по факту, раз это подписка

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.author.recipes.all()

        if recipes_limit is not None and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]

        return RecipeShortSerializer(recipes, many=True, context=self.context).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()





