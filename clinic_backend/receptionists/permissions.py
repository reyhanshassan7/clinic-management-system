from rest_framework.permissions import BasePermission


class IsReceptionist(BasePermission):
    """
    Allows access only to active receptionist staff.
    """

    def has_permission(self, request, view):

        # User must be logged in
        if not request.user or not request.user.is_authenticated:
            return False

        # Get Staff record
        try:
            staff = request.user.staff
        except Exception:
            return False

        # Staff must be active
        if not staff.is_active:
            return False

        # Staff must have a role
        if not staff.role:
            return False

        # Role must be Receptionist
        if staff.role.role_name != "Receptionist":
            return False

        # Receptionist profile must exist
        try:
            receptionist = staff.receptionist
        except Exception:
            return False

        # Receptionist must be active
        if not receptionist.is_active:
            return False

        return True