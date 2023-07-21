from django.test import TestCase
from .models import QuotaHistory, SubscriptionEvent, RedemptionEvent, DividendReceiveEvent, DividendPayEvent
from common.tests import CommonSetupMixin
from portfolios.models import PortfolioInvestment
from django.db.models import Sum
from cashflow.models import CurrencyTransaction
from django.core.exceptions import ObjectDoesNotExist
import time

class SubscriptionEventTestCase(CommonSetupMixin, TestCase):
    def create_subscription_event_test(self):
        return SubscriptionEvent.objects.create(
            portfolio=self.portfolio, 
            broker=self.broker_banco_brasil, 
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
        event = SubscriptionEvent.objects.create(
            portfolio=self.portfolio, 
            broker=self.broker_banco_brasil, 
            transaction_amount=transaction_amount, 
            price_brl=1.0,
            price_usd=0.20,
        )
        time.sleep(1)  # espera 1 segundo antes de criar o próximo evento
        return event
        
    def test_create_multiple_subscription_events(self):
        # Create multiple subscription events
        self.create_subscription_event_test(1000)        
        self.create_subscription_event_test(2000)
        self.create_subscription_event_test(1500)

        # Retrieve the corresponding QuotaHistory objects
        quota_histories = QuotaHistory.objects.filter(
            portfolio=self.portfolio,
            event_type='deposit',
        ).order_by('id')

        # Verify the quota_amount for each QuotaHistory
        self.assertEqual(quota_histories[0].quota_amount, 1000)
        self.assertEqual(quota_histories[1].quota_amount, 3000)
        self.assertEqual(quota_histories[2].quota_amount, 4500)

class RedemptionEventTestCase(CommonSetupMixin, TestCase):
    def setUp(self):
        super().setUp()
        SubscriptionEvent.objects.create(
            portfolio=self.portfolio, 
            broker=self.broker_banco_brasil, 
            transaction_amount=3000, 
            price_brl=1.0,
            price_usd=0.20,
        )

    def create_redemption_event_test(self, transaction_amount):
        return RedemptionEvent.objects.create(
            portfolio=self.portfolio, 
            broker=self.broker_banco_brasil, 
            transaction_amount=transaction_amount, 
            price_brl=1.0,
            price_usd=0.20,
        )

    def test_create_redemption_event(self):
        redemption_event = self.create_redemption_event_test(1000)
        self.assertEqual(redemption_event.portfolio, self.portfolio)
        self.assertEqual(redemption_event.broker, self.broker_banco_brasil)
        self.assertEqual(redemption_event.transaction_type, 'withdraw')
        self.assertEqual(redemption_event.transaction_amount, 1000)

    def test_create_currency_transaction(self):
        redemption_event = self.create_redemption_event_test(1000)

        corresponding_currency_transaction = CurrencyTransaction.objects.get(id=redemption_event.id)

        self.assertEqual(corresponding_currency_transaction.portfolio, self.portfolio)
        self.assertEqual(corresponding_currency_transaction.broker, self.broker_banco_brasil)
        self.assertEqual(corresponding_currency_transaction.transaction_type, 'withdraw')
        self.assertEqual(corresponding_currency_transaction.transaction_amount, 1000)

    def test_create_quota_history(self):
        self.create_redemption_event_test(1000)

        corresponding_quota_history = QuotaHistory.objects.get(
            portfolio=self.portfolio,
            event_type='withdraw',
        )

        self.assertEqual(corresponding_quota_history.portfolio, self.portfolio)
        self.assertEqual(corresponding_quota_history.event_type, 'withdraw')
        self.assertEqual(corresponding_quota_history.total_brl, 2000) # 3000 - 1000
        self.assertEqual(corresponding_quota_history.total_usd, 400) # 600 - 200
        self.assertEqual(corresponding_quota_history.quota_amount, 2000) # 3000 - 1000
        self.assertEqual(corresponding_quota_history.quota_price_brl, 1) # 2000 / 2000
        self.assertEqual(corresponding_quota_history.quota_price_usd, 0.2) # 400 / 2000
        self.assertEqual(corresponding_quota_history.percentage_change, 0) # since this is the first withdrawal

    def test_create_multiple_redemption_events(self):
        self.create_redemption_event_test(1000)        
        self.create_redemption_event_test(500)
        self.create_redemption_event_test(700)

        quota_histories = QuotaHistory.objects.filter(
            portfolio=self.portfolio,
            event_type='withdraw',
        ).order_by('id')

        self.assertEqual(quota_histories[0].quota_amount, 2000)
        self.assertEqual(quota_histories[1].quota_amount, 1500)
        self.assertEqual(quota_histories[2].quota_amount, 800)


class DividendReceiveEventTestCase(CommonSetupMixin, TestCase):
    def setUp(self):
        super().setUp()
        SubscriptionEvent.objects.create(
            portfolio=self.portfolio, 
            broker=self.broker_banco_brasil, 
            transaction_amount=3000, 
            price_brl=1.0,
            price_usd=0.20,
        )

    def create_dividend_receive_event_test(self, transaction_amount):
        event = DividendReceiveEvent(
            portfolio=self.portfolio, 
            broker=self.broker_banco_brasil, 
            transaction_amount=transaction_amount,
            price_brl=1.0,
            price_usd=0.20,
        )
        event.save() # This will also trigger create_quota_history()
        return event

    def test_create_dividend_receive_event(self):
        dividend_receive_event = self.create_dividend_receive_event_test(300)

        self.assertEqual(dividend_receive_event.portfolio, self.portfolio)
        self.assertEqual(dividend_receive_event.broker, self.broker_banco_brasil)
        self.assertEqual(dividend_receive_event.transaction_type, 'deposit')
        self.assertEqual(dividend_receive_event.transaction_amount, 300)

    def test_create_quota_history(self):
        self.create_dividend_receive_event_test(300)

        # Retrieve the corresponding QuotaHistory object
        corresponding_quota_history = QuotaHistory.objects.get(
            portfolio=self.portfolio,
            event_type='dividend receive',
        )

        self.assertEqual(corresponding_quota_history.portfolio, self.portfolio)
        self.assertEqual(corresponding_quota_history.event_type, 'dividend receive')
        self.assertEqual(corresponding_quota_history.value_brl, 300)
        self.assertEqual(corresponding_quota_history.value_usd, 60)
        self.assertEqual(corresponding_quota_history.total_brl, 3300) # 3000 initial + 100 dividend
        self.assertEqual(corresponding_quota_history.total_usd, 660) # 600 initial + 20 dividend
        self.assertEqual(corresponding_quota_history.quota_amount, 3000) # Same as initial deposit
        self.assertEqual(corresponding_quota_history.quota_price_brl, 1.1) # total_brl / quota_amount, 3300/3000=1.1
        self.assertEqual(corresponding_quota_history.quota_price_usd, 0.22) # total_usd / quota_amount, 660/3000=0.22
        self.assertNotEqual(corresponding_quota_history.percentage_change, 0) # There should be a change
        self.assertAlmostEqual(corresponding_quota_history.percentage_change, 0.1, places=7) # (total_brl / quota_amount) - 1, 1.1 - 1 = 0.1

class DividendPayEventTestCase(CommonSetupMixin, TestCase):
    def setUp(self):
        super().setUp()
        SubscriptionEvent.objects.create(
            portfolio=self.portfolio, 
            broker=self.broker_banco_brasil, 
            transaction_amount=3000, 
            price_brl=1.0,
            price_usd=0.20,
        )

    def create_dividend_pay_event_test(self, transaction_amount):
        event = DividendPayEvent(
            portfolio=self.portfolio, 
            broker=self.broker_banco_brasil, 
            transaction_amount=transaction_amount,
            price_brl=1.0,
            price_usd=0.20,
        )
        event.save() # This will also trigger create_quota_history()
        return event

    def test_create_dividend_pay_event(self):
        dividend_pay_event = self.create_dividend_pay_event_test(300)

        self.assertEqual(dividend_pay_event.portfolio, self.portfolio)
        self.assertEqual(dividend_pay_event.broker, self.broker_banco_brasil)
        self.assertEqual(dividend_pay_event.transaction_type, 'withdraw')
        self.assertEqual(dividend_pay_event.transaction_amount, 300)

    def test_create_quota_history(self):
        self.create_dividend_pay_event_test(300)

        # Retrieve the corresponding QuotaHistory object
        corresponding_quota_history = QuotaHistory.objects.get(
            portfolio=self.portfolio,
            event_type='dividend payment',
        )

        self.assertEqual(corresponding_quota_history.portfolio, self.portfolio)
        self.assertEqual(corresponding_quota_history.event_type, 'dividend payment')
        self.assertEqual(corresponding_quota_history.value_brl, -300)
        self.assertEqual(corresponding_quota_history.value_usd, -60)
        self.assertEqual(corresponding_quota_history.total_brl, 2700) # 3000 initial - 300 dividend
        self.assertEqual(corresponding_quota_history.total_usd, 540) # 600 initial - 60 dividend
        self.assertEqual(corresponding_quota_history.quota_amount, 3000) # Same as initial deposit
        self.assertEqual(corresponding_quota_history.quota_price_brl, 0.9) # total_brl / quota_amount, 2700/3000=0.9
        self.assertEqual(corresponding_quota_history.quota_price_usd, 0.18) # total_usd / quota_amount, 540/3000=0.18
        self.assertNotEqual(corresponding_quota_history.percentage_change, 0) # There should be a change
        self.assertAlmostEqual(corresponding_quota_history.percentage_change, - 0.1, places=7) # (total_brl / quota_amount) - 1, 0.9 - 1 = -0.1












