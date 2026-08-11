from rest_framework import permissions

class IsOwnerorReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
    
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
    
