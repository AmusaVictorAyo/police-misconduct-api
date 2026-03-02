from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrOversight(BasePermission):
    """
    - Citizens can only access their own complaints.
    - Oversight/Admin (staff/superuser) can access any complaint.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Allow staff/admin to do anything
        if user and (user.is_staff or user.is_superuser):
            return True

        # Otherwise only the owner can access
        return obj.user == user


class IsOversightOrAdmin(BasePermission):
    """
    Only Oversight/Admin can change status / route complaints.
    For MVP, we treat staff/superuser as oversight/admin.
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(user and (user.is_staff or user.is_superuser))