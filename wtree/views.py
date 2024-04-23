# wtree/views.py

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import MetaMaskRegistrationSerializer, MetaMaskLoginSerializer
from djoser.utils import login_user

User = get_user_model()

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
            user = User.objects.get(username=serializer.validated_data['address'])
            if user:
                login_user(request, user)  # Djoser handles login and token creation
                token = user.auth_token.key  # Access the token created by Djoser
                return Response({
                    'token': token,
                    'user_id': user.pk,
                    'message': 'Login via MetaMask successful!'
                }, status=status.HTTP_200_OK)
            else:
                return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class MetaMaskLoginView(APIView):
#     def post(self, request):
#         serializer = MetaMaskLoginSerializer(data=request.data)
#         if serializer.is_valid():
#             username = serializer.validated_data['address']
#             # Buscar o usuário diretamente, pois a autenticação da assinatura já foi feita
#             try:
#                 user = User.objects.get(username=username)
#                 login_user(request, user)
#                 token = settings.TOKEN_MODEL.objects.create(user=user)
#                 return Response({
#                     'token': str(token),
#                     'user_id': user.pk,
#                     'message': 'Login via MetaMask successful!'
#                 }, status=status.HTTP_200_OK)
#             except User.DoesNotExist:
#                 print(f"User not found with address: {username}")
#                 return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             print(f"Serializer errors: {serializer.errors}")
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
