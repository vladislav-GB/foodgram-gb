from django.shortcuts import render
from recipes.models import Recipe


def recipe_list(request):
    recipes = Recipe.objects.all()
    context = {"recipes": recipes}
    return render(request, "recipes/recipe_list.html", context)
