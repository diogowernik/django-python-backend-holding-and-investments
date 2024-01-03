from rest_framework.permissions import BasePermission

# apenas owner pode CRUD
class IsOwner(BasePermission):
    """
    Custom permission to only allow owners of an object to perform CRUD operations.
    """

    def has_permission(self, request, view):
        # Verifica se o usuário está autenticado
        if not request.user or not request.user.is_authenticated:
            return False

        # Permite requisições POST por qualquer usuário autenticado
        if request.method == 'POST':
            return True

        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        # Permite operações CRUD apenas ao dono do objeto
        return obj.owner == request.user

# todos podem ler e apenas owner podem escrever
class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to allow anyone to read an object, but only owners can perform write operations.
    """

    def has_object_permission(self, request, view, obj):
        # Leitura permitida para qualquer um
        if request.method in permissions.SAFE_METHODS:
            return True

        # Escrita apenas pelo dono do objeto
        return obj.owner == request.user

