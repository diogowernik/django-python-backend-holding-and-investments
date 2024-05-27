from django.db import models

class Blockchain(models.Model):
    name = models.CharField(max_length=50) # Ex: Ethereum, Binance Smart Chain, Bitcoin
    slug = models.SlugField()
    icon_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class CryptoBase(models.Model):
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10)
    blockchain = models.ForeignKey('Blockchain', on_delete=models.CASCADE)
    icon_url = models.URLField(blank=True, null=True)
    slug = models.SlugField()

# USDT, USDC, DAI, etc
class Token(CryptoBase):
    contract_address = models.CharField(max_length=42)  # Endereço típico do Ethereum
    decimals = models.IntegerField(default=18)

    def __str__(self):
        return f"{self.name} ({self.symbol}) on {self.blockchain}"

# Ethereum, Binance Coin, Bitcoin, etc
class Native(CryptoBase):

    def __str__(self):
        return f"{self.name} ({self.symbol}) on {self.blockchain}"
