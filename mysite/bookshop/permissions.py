from rest_framework.permissions import BasePermission


class IsSuperuser(BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        return request.user.is_superuser


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff