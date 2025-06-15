from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import UserAvatarView

from . import views

router = DefaultRouter()
router.register("ingredients", views.IngredientViewSet, basename="ingredients")
router.register("recipes", views.RecipeViewSet, basename="recipes")
router.register("users", views.UserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path("users/me/avatar/", UserAvatarView.as_view(), name="user-avatar"),
]
