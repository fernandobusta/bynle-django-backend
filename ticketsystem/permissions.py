from rest_framework.permissions import BasePermission

class IsTicketScannerUser(BasePermission):
    """
    Allows access only to ticket scanner users.
    """

    def has_permission(self, request, view):
        return request.user.user_type == 'ticket_scanner'