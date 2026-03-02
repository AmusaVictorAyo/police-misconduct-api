from rest_framework.permissions import BasePermission


def get_role(user) -> str:
    """
    Safely get the role from user.profile.role.
    Default to CITIZEN if profile/role doesn't exist.
    """
    try:
        return getattr(user.profile, "role", "CITIZEN") or "CITIZEN"
    except Exception:
        return "CITIZEN"


def is_oversight_or_admin(user) -> bool:
    """
    Treat staff/superuser as admin.
    Also treat profile roles as oversight/admin for tests/reviewer pack.
    """
    if not user or not user.is_authenticated:
        return False

    if user.is_staff or user.is_superuser:
        return True

    role = get_role(user)
    return role in {"OVERSIGHT", "ADMIN"}


class IsOwnerOrOversight(BasePermission):
    """
    - Owner can access their complaint
    - Oversight/Admin can access any complaint
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if is_oversight_or_admin(user):
            return True

        return obj.user == user


class IsOversightOrAdmin(BasePermission):
    """
    Only Oversight/Admin can change status / route complaints.
    """

    def has_permission(self, request, view):
        return is_oversight_or_admin(request.user)