# wtree/models.py

from django.db import models
from django.contrib.auth.models import User
    
class WtreeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    username = models.CharField(max_length=50, unique=True) # no frontend será algo do tipo https://wtr.ee/user.name
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    theme_options = [
        ('defautTheme', 'Default Theme'),
        ('lightTheme', 'Light Theme'),
    ]
    theme = models.CharField(max_length=50, default='defaultTheme', choices=theme_options)

    accepted_cryptos = models.ManyToManyField('blockchains.CriptoBase', related_name='profiles', blank=True) # base cryptos that this profile uses, initially it will be only one base crypto per profile, ethereum (matic, bnb and eth), but need to think for example in bitcoin or fiat base cryptos in same profile.
    wallets = models.ManyToManyField('Wallet', related_name='profiles', blank=True) # wallets that this profile uses, initially it will be only one wallet per profile, ethereum wallet (matic, bnb and eth), but need to think for example in bitcoin or fiat wallets in same profile.

    def __str__(self):
        return f"{self.user.username}"

class Wallet(models.Model):
    # Only one wallet per user initially, and only ETH based wallets (Matic, BNB and ETH) for the MVP
    type_options = [
        ('EHT based', 'Ethereum based'), # ETH, BNB, MATIC
        # ('Bitcoin', 'Bitcoin'), Not implemented yet, but don`t delete this, it will be useful in the future
        # ('Fiat', 'Fiat'), Not implemented yet, but don`t delete this, it will be useful in the future
    ]

    type = models.CharField(max_length=50, default='Ethereum based', choices=type_options) # ethereum based, bitcoin, fiat, etc
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=42)  # Endereços Ethereum têm 42 caracteres

    def __str__(self):
        return f"{self.user.username} - {self.address}"



