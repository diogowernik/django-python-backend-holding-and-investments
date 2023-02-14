from django.db import models
from brokers.models import Broker
from portfolios.models import Portfolio
# Create your models here.

class Income(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.CharField(max_length=255)
    amount = models.FloatField(default=0)

    def __str__(self):
        return f"{self.description} - {self.amount}"

class Expense(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.CharField(max_length=255)
    amount = models.FloatField(default=0)

    def __str__(self):
        return f"{self.description} - {self.amount}"