# Estou planejando implementar um sistema de autenticação em meu aplicativo Django, utilizando a biblioteca Djoser para gerenciamento de tokens. 
# Será hibrido, podendo usar o sistema de autenticação padrão do Djoser ou autenticação via Metamask.
# O sistema via djoser já está implementado e funcionando, porém estou com dificuldades para implementar o sistema de autenticação via Metamask.
# A ideia é autenticar usuários através do Metamask, onde o "username" será o endereço da carteira de criptomoedas do usuário. Pretendo usar uma assinatura digital como método de autenticação. Sei que o Djoser normalmente utiliza senha, e estou avaliando como integrar isso.  Já comecei algo mas me perdi, poderia usar o Djoser que estudamos agora e avaliar os aquivos que compartilhei aqui.

# meu serializer

from django.contrib.auth import get_user_model
from rest_framework import serializers
from eth_account.messages import encode_defunct
from eth_account import Account
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from djoser.serializers import TokenCreateSerializer as DjoserTokenCreateSerializer

User = get_user_model()

class MetaMaskRegistrationSerializer(DjoserUserCreateSerializer):
    address = serializers.CharField(max_length=42)
    signature = serializers.CharField(max_length=132, required=False)

    def validate_address(self, address):
        if User.objects.filter(username=address).exists():
            raise serializers.ValidationError("This address is already registered.")
        return address

    def validate(self, data):
        address = data['address']
        signature = data.get('signature')
        if signature:
            message = "Please sign this message to confirm your registration."
            message_hash = encode_defunct(text=message)
            try:
                signer = Account.recover_message(message_hash, signature=signature)
                if signer.lower() != address.lower():
                    raise serializers.ValidationError("Signature does not match the provided address.")
            except ValueError:
                raise serializers.ValidationError("Invalid signature.")
        return data

    def create(self, validated_data):
        address = validated_data['address']
        user = User.objects.create_user(username=address, password=None)  # no password set
        return user

class MetaMaskLoginSerializer(DjoserTokenCreateSerializer):
    address = serializers.CharField(max_length=42)
    signature = serializers.CharField(max_length=132)

    def validate(self, data):
        address = data['address']
        signature = data['signature']
        message = "Please sign this message to confirm your identity."
        message_hash = encode_defunct(text=message)
        try:
            signer = Account.recover_message(message_hash, signature=signature)
            if signer.lower() != address.lower():
                raise serializers.ValidationError("Signature does not match the provided address.")
        except ValueError:
            raise serializers.ValidationError("Invalid signature.")

        # Check if user exists
        if not User.objects.filter(username=address).exists():
            raise serializers.ValidationError("No user found with this address.")
        
        return data


# meu view

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import MetaMaskLoginSerializer, MetaMaskRegistrationSerializer
from djoser.utils import login_user
from djoser.conf import settings

class MetaMaskRegisterView(APIView):
    def post(self, request):
        serializer = MetaMaskRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created successfully.", "username": user.username}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MetaMaskLoginView(APIView):
    def post(self, request):
        serializer = MetaMaskLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['address'])
            if user:
                token = login_user(request, user)
                token_serializer_class = settings.SERIALIZERS.token
                return Response(
                    data=token_serializer_class(token).data, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# meus urls.py
from django.urls import path
from .views import MetaMaskRegisterView, MetaMaskLoginView
from djoser.views import (TokenCreateView)


urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/token/login/', TokenCreateView.as_view(), name='login'),
    path('auth/metamask/register/', MetaMaskRegisterView.as_view(), name='register_with_metamask'),
    path('auth/metamask/login/', MetaMaskLoginView.as_view(), name='login_with_metamask'),
    # Outras urls...
]