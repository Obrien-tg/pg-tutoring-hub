from rest_framework import permissions


class IsParentUser(permissions.BasePermission):
    message = "Parent access is required."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_parent
