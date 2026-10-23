from rest_framework.permissions import BasePermission


class HasStaffRole(BasePermission):
    allowed_roles = ()

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        staff = getattr(user, 'staff', None)
        return bool(
            staff and staff.is_active
            and staff.role and staff.role.is_active
            and staff.role.role_name in self.allowed_roles
        )


class IsPharmacist(HasStaffRole):
    allowed_roles = ('Pharmacist',)


class IsAdminOrPharmacist(HasStaffRole):
    allowed_roles = ('Admin', 'Pharmacist')

class IsAdmin(HasStaffRole):
    allowed_roles = ('Admin',)