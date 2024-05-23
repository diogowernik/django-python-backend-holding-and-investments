# contracts/models/transfer_gateway/models.py

from django.db import models
from blockchains.models import Token, Native, Blockchain
from wtree.models import Wallet # Wallet seriam as "Accounts" ex: wallet.address
from simple_history.models import HistoricalRecords

# TransferGateway Contract
class TransferBase(models.Model):
    sender = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='%(class)s_sent_transactions')
    recipient = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='%(class)s_received_transactions')
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    fee = models.DecimalField(max_digits=19, decimal_places=4)
    timestamp = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    gas_used = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        abstract = False  # Mantenha como False para criar uma tabela no banco de dados

class TransferNative(TransferBase):
    native = models.ForeignKey(Native, on_delete=models.CASCADE)  # Referência ao modelo Native

    def __str__(self):
        return f"From {self.sender} to {self.recipient} - {self.amount} {self.native.symbol}"

class TransferToken(TransferBase):
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    is_allowed = models.BooleanField(default=True)

    def __str__(self):
        status = "allowed" if self.is_allowed else "not allowed"
        return f"From {self.sender} to {self.recipient} - {self.amount} {self.token.symbol} ({status})"


