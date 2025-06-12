from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешает безопасные методы (GET, HEAD, OPTIONS) всем.
    Изменение/удаление — только автору объекта.
    Создание — только авторизованным пользователям.
    """

    def has_permission(self, request, view):
        # Разрешаем безопасные методы всем
        if request.method in SAFE_METHODS:
            return True

        # Создание (POST) разрешено только авторизованным
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user
