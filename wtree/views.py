# views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from web3 import Web3
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

@api_view(['POST'])
def authenticate_metamask(request):
    address = request.data.get('address')
    signature = request.data.get('signature')
    message = "Please sign this message to log in."

    # Usar web3.py para recuperar o endereço que assinou a mensagem
    w3 = Web3(Web3.HTTPProvider('YOUR_PROVIDER_URL'))
    signer = w3.eth.account.recover_message(text=message, signature=signature)

    if signer.lower() == address.lower():
        # O endereço é o mesmo que assinou a mensagem
        user, created = User.objects.get_or_create(username=address)
        token, created = Token.objects.get_or_create(user=user)

        return Response({'token': token.key}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)
