from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User

# Константы для валидации
COOKING_TIME_MIN = 1
COOKING_TIME_MAX = 32000
AMOUNT_MIN = 1
AMOUNT_MAX = 32000


class Ingredient(models.Model):
    name = models.CharField(
        "Название",
        max_length=200,
        help_text="Обязательно, не более 200 символов",
    )
    measurement_unit = models.CharField(
        "Единица измерения",
        max_length=200,
        help_text="Обязательно, укажите единицу измерения",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=("name", "measurement_unit"), name="unique_name_measurement"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class Recipe(models.Model):
    name = models.CharField(
        "Название",
        max_length=200,
        help_text="Обязательное, не более 200 символов",
    )
    image = models.ImageField(
        "",
        upload_to="recipes/images",
        help_text="Обязательно, добавьте изображение рецепта",
    )
    text = models.TextField(
        "Описание", help_text="Обязательно, опишите последовательность приготовления"
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredientsRelated",
        verbose_name="Ингредиенты",
        help_text="Обязательно, укажите ингредиенты",
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления",
        help_text="Обязательно, укажите время в минутах",
        validators=[
            MinValueValidator(COOKING_TIME_MIN),
            MaxValueValidator(COOKING_TIME_MAX),
        ],
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
        null=True,
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class RecipeIngredientsRelated(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient_recipes",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        "Количество",
        default=1,
        validators=[MinValueValidator(AMOUNT_MIN), MaxValueValidator(AMOUNT_MAX)],
    )

    class Meta:
        verbose_name = "Связь рецептов и ингредиентов"
        verbose_name_plural = "Связи рецептов и ингредиентов"
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "ingredient"), name="unique_recipe_ingredient"
            )
        ]

    def __str__(self):
        ingredient_name = self.ingredient.name if self.ingredient else "???"
        recipe_name = self.recipe.name if self.recipe else "???"
        return f"{self.amount} x {ingredient_name} для {recipe_name}"


class AbstractUserRecipeModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_user_recipe_relation"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.recipe.name}"


class ShoppingList(AbstractUserRecipeModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="shopping_cart",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="in_shopping_carts",
    )

    class Meta(AbstractUserRecipeModel.Meta):
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_shopping_list_user_recipe"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - список покупок: {self.recipe.name}"


class Favourite(AbstractUserRecipeModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="favorites",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="favorited_by",
    )

    class Meta(AbstractUserRecipeModel.Meta):
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_favourite_user_recipe"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - избранное: {self.recipe.name}"
