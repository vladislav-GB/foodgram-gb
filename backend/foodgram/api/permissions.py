from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешает безопасные методы (GET, HEAD, OPTIONS) всем,
    но запрещает изменение/удаление, если пользователь — не автор объекта.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем все безопасные методы
        if request.method in SAFE_METHODS:
            return True

        # Разрешаем изменение только автору объекта
        return obj.author == request.user
