# wtree/models.py

from django.db import models
from django.contrib.auth.models import User
from blockchains.models import Token, Native
    
class WtreeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    username = models.CharField(max_length=50, unique=True) # no frontend será algo do tipo https://wtr.ee/user.name
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    selected_networks = models.ManyToManyField('Network', related_name='profiles_selected', blank=True) # networks that user accepts to receive tokens or natives
    selected_natives = models.ManyToManyField('Native', related_name='profiles_selected', blank=True) # natives that user accepts to receive
    selected_tokens = models.ManyToManyField('Token', related_name='profiles_selected', blank=True) # tokens that user accepts to receive
    wallets = models.ManyToManyField('Wallet', related_name='profiles', blank=True) # wallets that this profile uses, initially it will be only one wallet per profile, ethereum wallet (matic, bnb and eth), but need to think for example in bitcoin or fiat wallets in same profile.

    def __str__(self):
        return f"{self.user.username}"

class Wallet(models.Model):
    type_options = [
        ('EHT based', 'Ethereum based'), # ETH, BNB, MATIC
        ('Bitcoin', 'Bitcoin'),
        ('Fiat', 'Fiat'),
        # Add more options here if needed
    ]

    type = models.CharField(max_length=50, default='Ethereum')  # Tipo de carteira, como "Ethereum", "Binance Smart Chain", "Polygon"
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=42)  # Endereços Ethereum têm 42 caracteres

    def __str__(self):
        return f"{self.user.username} - {self.address}"



