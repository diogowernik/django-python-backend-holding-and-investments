# wtree/views.py

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import MetaMaskRegistrationSerializer, MetaMaskLoginSerializer, MetaMaskAuthSerializer
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

class MetaMaskAuthView(APIView):
    def post(self, request):
        serializer = MetaMaskAuthSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(request=request)
            token = user.auth_token.key  # Assumes that Djoser handles token creation on login
            return Response({
                'token': token,
                'user_id': user.pk,
                'message': 'Login/Registration via MetaMask successful!'
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
