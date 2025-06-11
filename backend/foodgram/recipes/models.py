from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
        help_text='Обязательно, не более 200 символов',
    )
    measurement = models.CharField(
        'Единица измерения',
        max_length=200,
        help_text='Обязательно, укажите единицу измерения',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement'),
                name='unique_name_measurement'
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.measurement})'


class Recipe(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
        help_text='Обязательное, не более 200 символов',
    )
    image = models.ImageField(
        '',
        upload_to='recipes/images',
        help_text='Обязательно, добавьте изображение рецепта'
    )
    text = models.TextField(
        'Описание',
        help_text='Обязательно, опишите последовательность приготовления'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredientsRelated',
        verbose_name='',
        help_text='Обязательно, укажите ингредиенты',
    )
    cooking_time = models.IntegerField(
        'Время приготовления',
        help_text='Обязательно, укажите время в минутах',
        validators=(MaxValueValidator(180), MinValueValidator(15)),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        null=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self):
        return self.name


class RecipeIngredientsRelated(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
    Ingredient,
    on_delete=models.CASCADE,
    related_name='recipe_ingredients',
    verbose_name='Ингредиент',
    default=1,  # например, 1 — id ингредиента, который точно есть
    )
    count = models.IntegerField(
        'Количество',
        validators=(MinValueValidator(1), MaxValueValidator(1000)),
    )

    class Meta:
        verbose_name = 'Связь рецептов и ингредиентов'
        verbose_name_plural = 'Связи рецептов и ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            ),
        ]

    def __str__(self):
        return f'{self.count} x {self.ingredient.name} для {self.recipe.name}'


class AbstractUserRecipeModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe_relation'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class ShoppingList(AbstractUserRecipeModel):

    class Meta(AbstractUserRecipeModel.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_list_user_recipe'
            )
        ]

    # Опционально можно добавить related_name через переопределение user и recipe, если нужно


class Favourite(AbstractUserRecipeModel):

    class Meta(AbstractUserRecipeModel.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favourite_user_recipe'
            )
        ]

