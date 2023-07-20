from django.test import TestCase
from django.contrib.auth.models import User
from .models import Portfolio, QuotaHistory, SubscriptionEvent, PortfolioHistory    
from common.tests import CommonSetupMixin
from portfolios.models import PortfolioInvestment
from django.db.models import Sum
from cashflow.models import CurrencyTransaction
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta

# Campos do QuotaHistory:
# portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, default=11)
# event_type = models.CharField( ... default='deposit'
# value_brl = models.FloatField(default=0) # Exemplo: 1000 reais
# value_usd = models.FloatField(default=0) # Exemplo: 200 dolares (200 * 5 = 1000 reais)
# date = models.DateTimeField(default=datetime.now, editable=False) # sempre vai ser uma foto do momento, gravado em pedra.
# total_brl = models.FloatField(default=0, editable=False)
# total_usd = models.FloatField(default=0, editable=False)
# quota_amount = models.FloatField(default=0, editable=False)
# quota_price_brl = models.FloatField(default=0, editable=False)
# quota_price_usd = models.FloatField(default=0, editable=False)
# percentage_change = models.FloatField(default=0, editable=False)

class SubscriptionEventTestCase(CommonSetupMixin, TestCase):
    def create_subscription_event_test(self):
        return SubscriptionEvent.objects.create(
            portfolio=self.portfolio, 
            broker=self.broker_banco_brasil, 
            transaction_type='deposit', 
            transaction_amount=1000, 
            price_brl=1.0,
            price_usd=0.20,
        )
    
    # verifica se o evento de subscription foi criado corretamente
    def test_create_subscription_event(self):
        subscription_event = self.create_subscription_event_test()
        self.assertEqual(subscription_event.portfolio, self.portfolio)
        self.assertEqual(subscription_event.broker, self.broker_banco_brasil)
        self.assertEqual(subscription_event.transaction_type, 'deposit')
        self.assertEqual(subscription_event.transaction_amount, 1000)

    def test_create_currency_transaction(self):
        subscription_event = self.create_subscription_event_test()

        # Retrieve the corresponding CurrencyTransaction object
        corresponding_currency_transaction = CurrencyTransaction.objects.get(id=subscription_event.id)

        # Verify the values are the same
        self.assertEqual(corresponding_currency_transaction.portfolio, self.portfolio)
        self.assertEqual(corresponding_currency_transaction.broker, self.broker_banco_brasil)
        self.assertEqual(corresponding_currency_transaction.transaction_type, 'deposit')
        self.assertEqual(corresponding_currency_transaction.transaction_amount, 1000)
    
    # Verifica se foi criado um QuotaHistory
    def test_create_quota_history(self):
        self.create_subscription_event_test()

        # Retrieve the corresponding CurrencyTransaction object
        corresponding_quota_history = QuotaHistory.objects.get(
            portfolio=self.portfolio,
            event_type='deposit',
        )

        # Verify the values are the same
        self.assertEqual(corresponding_quota_history.portfolio, self.portfolio)
        self.assertEqual(corresponding_quota_history.event_type, 'deposit')
        self.assertEqual(corresponding_quota_history.total_brl, 1000) # 1000 * 1
        self.assertEqual(corresponding_quota_history.total_usd, 200) # 1000 * 0.2 broker.main_currency.price_usd
        self.assertEqual(corresponding_quota_history.quota_amount, 1000) # 1000 * 1
        self.assertEqual(corresponding_quota_history.quota_price_brl, 1) # 1000 * 1 / 1000
        self.assertEqual(corresponding_quota_history.quota_price_usd, 0.2) # 1000 * 0.2 / 1000
        self.assertEqual(corresponding_quota_history.percentage_change, 0) # 1000 * 0.2 / 1000

        # Verifica se foi criado um PortfolioInvestment


class SubscriptionEventTestCase(CommonSetupMixin, TestCase):
    def create_subscription_event_test(self, transaction_amount):
        return SubscriptionEvent.objects.create(
            portfolio=self.portfolio, 
            broker=self.broker_banco_brasil, 
            transaction_type='deposit', 
            transaction_amount=transaction_amount, 
            price_brl=1.0,
            price_usd=0.20,
        )
        
    def test_create_multiple_subscription_events(self):
        # Create multiple subscription events
        self.create_subscription_event_test(1000)
        self.create_subscription_event_test(2000)
        self.create_subscription_event_test(1500)

        # Retrieve the corresponding QuotaHistory objects
        quota_histories = QuotaHistory.objects.filter(
            portfolio=self.portfolio,
            event_type='deposit',
        ).order_by('date')

        # Verify the quota_amount for each QuotaHistory
        self.assertEqual(quota_histories[0].quota_amount, 1000)  # 1000 (from the first transaction)
        self.assertEqual(quota_histories[1].quota_amount, 3000)  # 1000 + 2000 (from the first and second transactions)
        self.assertEqual(quota_histories[2].quota_amount, 4500)  # 1000 + 2000 + 1500 (from all transactions)



    












