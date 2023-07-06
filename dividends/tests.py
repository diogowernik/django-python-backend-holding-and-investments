from django.test import TestCase
from django.test import TestCase
from portfolios.models import PortfolioInvestment,Portfolio
from investments.models import CurrencyHolding, Stocks, BrStocks, Reit
from brokers.models import Broker, Currency 
from cashflow.models import CurrencyTransaction, AssetTransaction, CurrencyTransfer, InternationalCurrencyTransfer
from categories.models import Category, SubCategory
from dividends.models import Dividend, PortfolioDividend
from django.contrib.auth.models import User
from django.utils import timezone


class DividendsTestCase(TestCase):
    def setUp(self):
        self.currency_brl = Currency.objects.create(ticker='BRL', price_brl=1, price_usd=0.20)
        self.currency_usd = Currency.objects.create(ticker='USD', price_brl=5, price_usd=1)
        self.broker_banco_brasil= Broker.objects.create(name='Banco do Brasil', main_currency=self.currency_brl, slug='banco-do-brasil')
        self.broker_avenue= Broker.objects.create(name='Itau', main_currency=self.currency_usd, slug='avenue')
        self.broker_itau= Broker.objects.create(name='Itau', main_currency=self.currency_brl, slug='itau')

        # Configuração inicial. Criamos os objetos necessários para os testes.
        self.category = Category.objects.create(name='Test Category')
        self.subcategory = SubCategory.objects.create(name='Test SubCategory')
        self.asset_brl = CurrencyHolding.objects.create(ticker='BRL', category=self.category, subcategory=self.subcategory, currency=self.currency_brl, price_brl=1, price_usd=0.20)
        self.asset_usd = CurrencyHolding.objects.create(ticker='USD', category=self.category, subcategory=self.subcategory, currency=self.currency_usd, price_brl=5, price_usd=1)

        # Cria um usuário para ser o proprietário do portfolio
        self.user = User.objects.create_user(username='testuser', password='12345')
        # Cria um broker para ser usado nas trades

        self.portfolio = Portfolio.objects.create(name='Test Portfolio', owner=self.user)

        self.asset_wege3 = BrStocks.objects.create(ticker='WEGE3', category=self.category, subcategory=self.subcategory, price_brl=50, price_usd=10)
        self.asset_itub4 = BrStocks.objects.create(ticker='ITUB4', category=self.category, subcategory=self.subcategory, price_brl=30, price_usd=6)
        self.asset_msft = Stocks.objects.create(ticker='MSFT', category=self.category, subcategory=self.subcategory, price_brl=200, price_usd=40)
        self.asset_o = Reit.objects.create(ticker='O', category=self.category, subcategory=self.subcategory, price_brl=100, price_usd=20)

        # duas de compra
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
            record_date=(timezone.now() - timezone.timedelta(days=20)).date(),  # Convertendo datetime para date
            pay_date=(timezone.now() - timezone.timedelta(days=10)).date()  # Convertendo datetime para date
        )
        
        # Verifique se o dividendo foi criado
        self.assertEqual(dividend, Dividend.objects.latest('id'))

        # Verifique se um PortfolioDividend foi criado
        portfolio_dividend = PortfolioDividend.objects.filter(asset=self.asset_itub4).latest('id')
        self.assertIsNotNone(portfolio_dividend)

        # Verifique se o PortfolioDividend tem os valores corretos
        self.assertEqual(portfolio_dividend.value_per_share_brl, 2)
        self.assertEqual(portfolio_dividend.value_per_share_usd, 0.4)
        self.assertEqual(portfolio_dividend.record_date, dividend.record_date)
        self.assertEqual(portfolio_dividend.pay_date, dividend.pay_date)
        self.assertEqual(portfolio_dividend.shares_amount, 100)  # por ser 20 dias atrás, 100 + 100 - 100 = 100
    
 
    # def test_create_dividends_record_date_32_days_ago(self):
        # Criando um dividendo
        dividend = Dividend.objects.create(
            asset=self.asset_itub4, 
            value_per_share_brl=2, 
            value_per_share_usd=0.4, 
            record_date=(timezone.now() - timezone.timedelta(days=32)).date(),  # Convertendo datetime para date
            pay_date=(timezone.now() - timezone.timedelta(days=10)).date()  # Convertendo datetime para date
        )
        
        # Verifique se o dividendo foi criado
        self.assertEqual(dividend, Dividend.objects.latest('id'))

        # Verifique se um PortfolioDividend foi criado
        portfolio_dividend = PortfolioDividend.objects.filter(asset=self.asset_itub4).latest('id')
        self.assertIsNotNone(portfolio_dividend)

        # Verifique se o PortfolioDividend tem os valores corretos
        self.assertEqual(portfolio_dividend.value_per_share_brl, 2)
        self.assertEqual(portfolio_dividend.value_per_share_usd, 0.4)
        self.assertEqual(portfolio_dividend.record_date, dividend.record_date)
        self.assertEqual(portfolio_dividend.pay_date, dividend.pay_date)
        self.assertEqual(portfolio_dividend.shares_amount, 200)   # por ser 32 dias atrás, apenas a terceira transação não é considerada, então 100 + 100 = 200

 