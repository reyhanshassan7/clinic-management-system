from rest_framework.permissions import BasePermission


class IsReceptionist(BasePermission):
    """
    Allows access only to authenticated users
    whose Staff role is Receptionist.
    """

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        try:
            staff = request.user.staff

            if not staff.is_active:
                return False

            if not staff.role:
                return False

            return staff.role.role_name.lower() == "receptionist"

        except Exception:
            return False