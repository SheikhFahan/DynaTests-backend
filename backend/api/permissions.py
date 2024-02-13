from rest_framework import permissions
from django.core.exceptions import PermissionDenied

class IsInstituteAndOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return 'institute' in request.user.groups.values_list('name', flat=True)
    
    def has_object_permission(self, request, view, obj):
        # checks if the object belongs to the user 
        return  request.user == obj.user
    
class IsInstitute(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return 'institute' in request.user.groups.values_list('name', flat=True)
        raise PermissionDenied("User is not in the 'student' group.")    
    
class IsStudent(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return 'student' in request.user.groups.values_list('name', flat=True)
        raise PermissionDenied("User is not in the 'student' group.")    