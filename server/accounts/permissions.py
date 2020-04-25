from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS and request.user.is_authenticated:
            return True

        # Instance must have an attribute named `user`.
        if hasattr(obj, 'user'):
            return obj.user.pk == request.user.pk
        elif hasattr(obj, 'owner'):
            return obj.owner.pk == request.user.pk
        else:
            raise Exception("No owner field found.")


class IsUserOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated and (obj.pk == request.user.pk)


class UnauthenticatedOnly(permissions.BasePermission):
    """
    Checks whether user is unauthenticated.
    """

    def has_permission(self, request, view):
        return not request.user.is_authenticated