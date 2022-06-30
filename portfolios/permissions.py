import json
from rest_framework import permissions
from . import models


# Permission only user can CRUD

# class IsOwner(permissions.BasePermission):
#     """
#     Custom permission to only allow owners of an object to edit it.
#     """

#     def has_permission(self, request, view):
#         return request.user and request.user.is_authenticated()

#     def has_object_permission(self, request, view, obj):
#         return obj.user == request.user


# class IsOwnerOrReadOnly(permissions.BasePermission):

#   def has_object_permission(self, request, view, obj):
#     # Read permissions are allowed to any request,
#     # so we'll always allow GET, HEAD or OPTIONS requests.
#     if request.method in permissions.SAFE_METHODS:
#         return True

#     # Write permissions are only allowed to the owner.
#     return obj.owner == request.user

# class PortfolioOwnerOrReadOnly(permissions.BasePermission):

#   def has_object_permission(self, request, view, obj):
#     # Read permissions are allowed to any request,
#     # so we'll always allow GET, HEAD or OPTIONS requests.
#     if request.method in permissions.SAFE_METHODS:
#         return True

#     # Write permissions are only allowed to the owner of the portfolio.
#     return obj.portfolio.owner == request.user

#   def has_permission(self, request, view):
#     try:
#       if request.method == "POST":
#         # For create action
#         data = json.loads(request.body)
#         models.Portfolio.objects.get(pk=data["portfolio"], owner_id=request.user.id)
#       return True
#     except:
#       return False
