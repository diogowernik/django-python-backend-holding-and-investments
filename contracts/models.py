from django.db import models
from blockchains.models import Token, Native, Network
from wtree.models import Wallet # Wallet seriam as "Accounts" ex: wallet.address
from simple_history.models import HistoricalRecords
 
# Create your models here.

class Contract(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=42)  # Endereço do contrato na blockchain
    abi = models.JSONField()  # ABI do contrato inteligente
    network = models.ForeignKey(Network, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} ({self.network})"

# TransferGateway Contract
from django.db import models
from blockchains.models import Token, Native, Network
from wtree.models import Wallet
from simple_history.models import HistoricalRecords

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


# TransferGateway Contract Admin, Esse pode ser apenas no admin, sem necessidade de ser no frontend

class FeeSetting(models.Model):
    fee_bps = models.PositiveIntegerField(default=50)  # Taxa inicial de 0.5%
    max_fee_bps = models.PositiveIntegerField(default=100)  # Limite máximo da taxa em base points (1.0%)

    def __str__(self):
        return f"Current fee: {self.fee_bps} bps, Max fee: {self.max_fee_bps} bps"

class AllowedToken(models.Model):
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    is_allowed = models.BooleanField(default=True)

    def __str__(self):
        status = "allowed" if self.is_allowed else "not allowed"
        return f"{self.token.name} ({self.token.symbol}) is {status}"

class ContractStatus(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    is_paused = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.contract.name}: {'Paused' if self.is_paused else 'Active'}"

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.save()
        # Aqui você também pode adicionar a lógica para interagir com o contrato inteligente
        # e efetivamente pausar ou despausar o contrato na blockchain.
