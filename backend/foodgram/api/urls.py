from django.urls import path, include
from .views import SetPasswordView
from users.views import UserAvatarView
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("ingredients", views.IngredientViewSet, basename="ingredients")
router.register("recipes", views.RecipeViewSet, basename="recipes")
router.register("users", views.UserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path("users/set_password/", SetPasswordView.as_view(), name="set-password"),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path("users/me/avatar/", UserAvatarView.as_view(), name="user-avatar"),
]
