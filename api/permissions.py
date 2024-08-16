from rest_framework import permissions

class IsAdminOrSelf(permissions.BasePermission):
 
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user or request.user.is_superuser
    
class IsSeller(permissions.BasePermission):
 
    def has_object_permission(self, request, view, obj):
        print(f"updating product for user: {obj.user.id} : {request.user.id}")

        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user.id == request.user.id or request.user.is_superuser  
