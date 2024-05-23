from django.db import models
from blockchains.models import Token, Native, Blockchain
from wtree.models import Wallet # Wallet seriam as "Accounts" ex: wallet.address
from simple_history.models import HistoricalRecords
 
# Create your models here.

class Contract(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=42)  # Endereço do contrato na blockchain
    abi = models.JSONField()  # ABI do contrato inteligente
    blockchain = models.ForeignKey(Blockchain, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} ({self.blockchain})"
