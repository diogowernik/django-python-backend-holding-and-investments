# contracts/models/contract_management/models.py

from django.db import models
from blockchains.models import Token, Native, Blockchain
from simple_history.models import HistoricalRecords
 

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
    contract = models.ForeignKey('Contract', on_delete=models.CASCADE)
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
