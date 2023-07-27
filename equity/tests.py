from django.test import TestCase
from common.tests import CommonSetupMixin
from equity.models import QuotaHistory, SubscriptionEvent, PortfolioTotalHistory, RedemptionEvent, InvestBrEvent, DividendReceiveEvent
from django.utils import timezone

class SubscriptionEventTest(CommonSetupMixin, TestCase):
    def setUp(self):
        super().setUp()

        self.subscription_event = SubscriptionEvent.objects.create(
            portfolio=self.portfolio,
            transaction_date=timezone.datetime(2006, 8, 28),
            transaction_amount=200000,
            price_brl=1,
            price_usd=0.45,
        )
    def test_quota_history_values_after_deposit(self):
        # Buscamos o objeto QuotaHistory relacionado ao depósito que criamos no setUp
        quota_history = QuotaHistory.objects.get(
            portfolio=self.portfolio,
            date=timezone.datetime(2006, 8, 28),
            event_type='deposit'
        )
        # Verificando todos os campos menos os que foram usados de critério de busca
        self.assertEqual(quota_history.value_brl, 200000)
        self.assertEqual(quota_history.value_usd, 90000)
        self.assertEqual(quota_history.total_brl, 200000)
        self.assertEqual(quota_history.total_usd, 90000)
        self.assertEqual(quota_history.quota_amount, 200000)
        self.assertEqual(quota_history.quota_price_brl, 1)
        self.assertEqual(quota_history.quota_price_usd, 0.45)

    # def test_subscription_again_one_month_after(self):
    #     self.subscription_event_2 = SubscriptionEvent.objects.create(
    #         portfolio=self.portfolio,
    #         transaction_date=timezone.datetime(2006, 9, 29),
    #         transaction_amount=10000,
    #         price_brl=1,
    #         price_usd=0.45,
    #     )
    #     quota_history = QuotaHistory.objects.get(
    #         portfolio=self.portfolio,
    #         date=timezone.datetime(2006, 9, 29),
    #         event_type='deposit'
    #     )

    #     self.assertEqual(quota_history.value_brl, 10000)
    #     self.assertEqual(quota_history.value_usd, 4500)
    #     self.assertEqual(quota_history.total_brl, 210000)
    #     self.assertEqual(quota_history.total_usd, 94500)
    #     self.assertEqual(quota_history.quota_amount, 210000)
    #     self.assertEqual(quota_history.quota_price_brl, 1)
    #     self.assertEqual(quota_history.quota_price_usd, 0.45)











