from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from users.models import User, Subscription


class CustomUserAdmin(UserAdmin):
    """Кастомный интерфейс админ-зоны для модели User."""

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)
    filter_horizontal = ()

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Персональная информация",
            {"fields": ("first_name", "last_name", "email", "avatar")},
        ),
        (
            "Права доступа",
            {
                "fields": ("is_active", "is_staff", "is_superuser"),
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscription)
# Отключаем стандартную группу, если не используется
admin.site.unregister(Group)
