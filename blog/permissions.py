from rest_framework import permissions

class IsOwnerorReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
    
class IsCommentAuthorOrPostOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        user = request.user

        #comment author
        if obj.author == user:
            return True
        
        if obj.post.author == user and request.method == 'DELETE':
            return True
        
        return user.is_staff==user
    
