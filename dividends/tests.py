from django.test import TestCase
from portfolios.models import PortfolioInvestment,Portfolio
from investments.models import CurrencyHolding, Stocks, BrStocks, Reit
from brokers.models import Broker, Currency 
from cashflow.models import CurrencyTransaction, AssetTransaction, CurrencyTransfer, InternationalCurrencyTransfer, TransactionsHistory
from categories.models import Category, SubCategory
from dividends.models import Dividend, PortfolioDividend
from django.contrib.auth.models import User
from django.utils import timezone
from common.tests import CommonSetupMixin

class DividendsTestCase(CommonSetupMixin, TestCase):
    def setUp(self):
        self.trade_1 = AssetTransaction.objects.create(
            portfolio=self.portfolio, broker=self.broker_banco_brasil, 
            transaction_type='buy', asset=self.asset_itub4, transaction_amount=100, price_brl=30, price_usd=6, 
            transaction_date=timezone.now() - timezone.timedelta(days=90))
        self.trade_2 = AssetTransaction.objects.create(
            portfolio=self.portfolio, broker=self.broker_banco_brasil, 
            transaction_type='buy', asset=self.asset_itub4, transaction_amount=100, price_brl=30, price_usd=6, 
            transaction_date=timezone.now() - timezone.timedelta(days=60))
        self.trade_3 = AssetTransaction.objects.create(
            portfolio=self.portfolio, broker=self.broker_banco_brasil, 
            transaction_type='sell', asset=self.asset_itub4, transaction_amount=100, price_brl=30, price_usd=6, 
            transaction_date=timezone.now() - timezone.timedelta(days=30))
        
    def test_create_dividends(self):
        # Criando um dividendo
        dividend = Dividend.objects.create(
            asset=self.asset_itub4, 
            value_per_share_brl=2, 
            value_per_share_usd=0.4, 
            record_date=(timezone.now() - timezone.timedelta(days=20)),  
            pay_date=(timezone.now() - timezone.timedelta(days=10))  
        )

        # Pode ser criado mais de um portfolio_dividend para o mesmo dividendo
        # Encontrar todos os portfolio_dividends que foram criados para o dividendo adicionado.
        portfolio_dividends = PortfolioDividend.objects.filter(dividend=dividend)
        self.assertTrue(portfolio_dividends.exists())



        for portfolio_dividend in portfolio_dividends:
            # Verifique se os PortfolioDividends tem os valores corretos
            self.assertEqual(portfolio_dividend.value_per_share_brl, 2)
            self.assertEqual(portfolio_dividend.value_per_share_usd, 0.4)
            self.assertEqual(portfolio_dividend.pay_date, dividend.pay_date)
            self.assertEqual(portfolio_dividend.shares_amount, 100)  # por ser 20 dias atrás, 100 + 100 - 100 = 100

    def test_create_dividends_40_days_ago(self):
        # Criando um dividendo
        dividend = Dividend.objects.create(
            asset=self.asset_itub4, 
            value_per_share_brl=2, 
            value_per_share_usd=0.4, 
            record_date=(timezone.now() - timezone.timedelta(days=40)),  
            pay_date=(timezone.now() - timezone.timedelta(days=10)) 
        )

        # Pode ser criado mais de um portfolio_dividend para o mesmo dividendo
        # Encontrar todos os portfolio_dividends que foram criados para o dividendo adicionado.
        portfolio_dividends = PortfolioDividend.objects.filter(dividend=dividend)
        self.assertTrue(portfolio_dividends.exists())

        for portfolio_dividend in portfolio_dividends:
            # Verifique se os PortfolioDividends tem os valores corretos
            self.assertEqual(portfolio_dividend.value_per_share_brl, 2)
            self.assertEqual(portfolio_dividend.value_per_share_usd, 0.4)
            self.assertEqual(portfolio_dividend.pay_date, dividend.pay_date)
            self.assertEqual(portfolio_dividend.shares_amount, 200)  # por ser 40 dias atrás, 100 + 100 = 100

    
 