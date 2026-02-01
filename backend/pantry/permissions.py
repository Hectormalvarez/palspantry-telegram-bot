from rest_framework import permissions
from django.conf import settings

class HasInternalAPIKey(permissions.BasePermission):
    """
    Permission class to check for internal API key authentication.
    """
    
    def has_permission(self, request, view):
        """
        Check if the request has a valid internal API key.
        """
        api_key = request.headers.get('X-API-KEY')
        return api_key == getattr(settings, 'INTERNAL_API_KEY', None)