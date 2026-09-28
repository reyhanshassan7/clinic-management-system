from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            staff = request.user.staff
        except:
            return False

        return (
            staff.is_active
            and staff.role
            and staff.role.role_name == "Admin"
        )