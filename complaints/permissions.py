from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrOversight(BasePermission):
    def has_object_permission(self, request, view, obj):
        role = getattr(request.user.profile, "role", "CITIZEN")

        if role in ("OVERSIGHT", "ADMIN"):
            return True

        return obj.user == request.user

class IsOversightOrAdmin(BasePermission):
    def has_permission(self, request, view):
        role = getattr(request.user.profile, "role", "CITIZEN")
        return role in ("OVERSIGHT", "ADMIN")