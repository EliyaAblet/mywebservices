# dogapp/permissions.py

from rest_framework import permissions
from graphql import GraphQLError


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to view it (for REST API).
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


def IsOwnerGQL(user, obj):
    """
    Custom permission for GraphQL to ensure the logged-in user owns the object.
    """
    if obj.owner != user:
        raise GraphQLError("You do not have appropriate permissions.")
