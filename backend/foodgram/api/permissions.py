from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Проверка на права доступа для Админа или только чтение."""
    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.is_admin
                or request.method in permissions.SAFE_METHODS)

class IsAuthorOrReadOnly(permissions.BasePermission):
    """Проверка на права доступа для Автора."""
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user