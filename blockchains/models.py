from django.db import models

class Network(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField()
    icon_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
from django.db import models

class CryptoBase(models.Model):
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10)
    blockchain = models.ForeignKey('Network', on_delete=models.CASCADE)
    icon_url = models.URLField(blank=True, null=True)
    slug = models.SlugField()

class Token(CryptoBase):
    contract_address = models.CharField(max_length=42)  # Endereço típico do Ethereum
    decimals = models.IntegerField(default=18)

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    class Meta:
        unique_together = ('contract_address', 'blockchain')
        verbose_name = "Token"
        verbose_name_plural = "Tokens"

class Native(CryptoBase):

    def __str__(self):
        return f"{self.name} ({self.symbol}) on {self.blockchain}"
