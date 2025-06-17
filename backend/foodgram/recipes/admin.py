from django.contrib import admin

from .models import (
    Favourite,
    Ingredient,
    Recipe,
    RecipeIngredientsRelated,
    ShoppingList,
)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)


class RecipeIngredientsRelatedInline(admin.TabularInline):
    model = RecipeIngredientsRelated
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "cooking_time")
    list_filter = ("author", "cooking_time")
    search_fields = ("name", "author__username")
    inlines = [RecipeIngredientsRelatedInline]
    readonly_fields = ("favorites_count",)

    def favorites_count(self, obj):
        return obj.favourites.count()

    favorites_count.short_description = "Добавлений в избранное"


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    list_filter = ("user",)


class FavouriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    list_filter = ("user",)
    search_fields = ("user__username", "recipe__name")


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredientsRelated)
admin.site.register(ShoppingList, ShoppingListAdmin)
admin.site.register(Favourite, FavouriteAdmin)
