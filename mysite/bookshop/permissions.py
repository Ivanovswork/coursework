from rest_framework.permissions import BasePermission


class IsSuperuser(BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        return request.user.is_superuser


class IsStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            return True
        return request.user.is_staff and request.user.company == obj.company
