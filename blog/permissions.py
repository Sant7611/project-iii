from rest_framework import permissions

class IsOwnerorReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class IsOwner(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return 
    
    def has_object_permission(self, request, view, obj):
        return request.user == obj.author
            
    
class IsAdminOrModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (user.role in ['moderator', 'admin'])
    
class IsCommentUserOrPostOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        user = request.user

        #comment user
        if obj.user == user:
            return True
        
        if obj.post.user == user and request.method == 'DELETE':
            return True
        
        return user.is_staff==user
    
