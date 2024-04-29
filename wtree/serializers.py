# wtree/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from eth_account.messages import encode_defunct
from eth_account import Account
from djoser.utils import login_user

User = get_user_model()

class MetaMaskRegistrationSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=42)
    signature = serializers.CharField(max_length=132, required=False)  # Opcional

    def validate(self, data):
        address = data.get('address')
        signature = data.get('signature')
        if signature:
            message = "Please sign this message to confirm your identity."
            message_hash = encode_defunct(text=message)
            try:
                signer = Account.recover_message(message_hash, signature=signature)
                if signer.lower() != address.lower():
                    raise serializers.ValidationError("Signature does not match the provided address.")
            except ValueError:
                raise serializers.ValidationError("Invalid signature.")
        return data

    def create(self, validated_data):
        address = validated_data.get('address')
        user = User.objects.create_user(username=address)
        return user

# wtree/serializers.py
class MetaMaskLoginSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=42)
    signature = serializers.CharField(max_length=132)

    def validate(self, data):
        address = data.get('address')
        signature = data.get('signature')
        message = "Please sign this message to confirm your identity."
        message_hash = encode_defunct(text=message)
        apelido = User.objects.filter(username=address)
        print("###")
        print(" Apelido: ", apelido)
        # console log
        print("###")
        print("message_hash", message_hash)
        print("###")
        print("signature", signature)
        print("###")
        print("address", address)
        try:
            signer = Account.recover_message(message_hash, signature=signature)
            if signer.lower() != address.lower():
                raise serializers.ValidationError("Signature does not match the provided address.")
        except ValueError:
            raise serializers.ValidationError("Invalid signature.")
        # Verificar se o usuário existe:
        if not User.objects.filter(username=address).exists():
            raise serializers.ValidationError("User not found.")
        return data

class MetaMaskAuthSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=42)
    signature = serializers.CharField(max_length=132)

    def validate(self, data):
        address = data['address']
        signature = data['signature']
        user_exists = User.objects.filter(username=address).exists()

        message = "Please sign this message to confirm your identity."

        message_hash = encode_defunct(text=message)
        try:
            signer = Account.recover_message(message_hash, signature=signature)
            if signer.lower() != address.lower():
                raise serializers.ValidationError("Signature does not match the provided address.")
        except ValueError:
            raise serializers.ValidationError("Invalid signature.")

        data['user_exists'] = user_exists
        return data

    def save(self, request):
        address = self.validated_data['address']
        user_exists = self.validated_data['user_exists']

        if user_exists:
            user = User.objects.get(username=address)
        else:
            user = User.objects.create_user(username=address)

        login_user(request, user)  # Use Djoser to handle login
        return user
