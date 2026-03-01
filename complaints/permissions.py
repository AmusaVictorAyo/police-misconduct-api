from rest_framework.permissions import BasePermission


def get_role(user):
    return getattr(getattr(user, "profile", None), "role", "CITIZEN")


class IsOwnerOrOversight(BasePermission):
    """
    Citizens can access only their own complaint.
    Oversight/Admin can access all complaints.
    """

    def has_object_permission(self, request, view, obj):
        role = get_role(request.user)
        if role in ("OVERSIGHT", "ADMIN"):
            return True
        return obj.user == request.user


class IsOversightOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return get_role(request.user) in ("OVERSIGHT", "ADMIN")