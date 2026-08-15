from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author_id == request.user.id
        )

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "super_admin"
        )


class IsModeratorOrSuperAdmin(permissions.BasePermission):
    allowed_roles = {"moderator", "super_admin"}

    def has_permission(self, request, view):
        user = request.user

        return (
            user.is_authenticated
            and user.role in self.allowed_roles
        )


class CanManageUser(IsModeratorOrSuperAdmin):
    def has_object_permission(self, request, view, obj):
        actor = request.user

        if actor.role == "super_admin":
            return (
                obj.role in {"user", "moderator"}
                and obj.pk != actor.pk
            )

        if actor.role == "moderator":
            return obj.role == "user"

        return False
    
    
class IsCommentUserOrPostOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        if not user.is_authenticated:
            return False

        if obj.author_id == user.id:
            return True

        if request.method == 'DELETE' and obj.post.author_id == user.id:
            return True

        return user.is_staff
    
