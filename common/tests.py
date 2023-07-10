from django.test import TestCase
from django.test import TestCase
from portfolios.models import PortfolioInvestment,Portfolio
from investments.models import CurrencyHolding, Stocks, BrStocks, Reit
from brokers.models import Broker, Currency 
from cashflow.models import CurrencyTransaction, AssetTransaction, CurrencyTransfer, InternationalCurrencyTransfer, TransactionsHistory
from categories.models import Category, SubCategory
from dividends.models import Dividend, PortfolioDividend
from django.contrib.auth.models import User
from django.utils import timezone

class CommonSetupMixin:
    @classmethod
    def setUpTestData(cls):
        # Setup comum para os testes Dividends e Cashflow
        cls.currency_brl = Currency.objects.create(ticker='BRL', price_brl=1, price_usd=0.20)
        cls.currency_usd = Currency.objects.create(ticker='USD', price_brl=5, price_usd=1)
        cls.currency_eur = Currency.objects.create(ticker='EUR', price_brl=6, price_usd=1.2)
        cls.broker_banco_brasil= Broker.objects.create(name='Banco do Brasil', main_currency=cls.currency_brl, slug='banco-do-brasil')
        cls.broker_avenue= Broker.objects.create(name='Avenue', main_currency=cls.currency_usd, slug='avenue')
        cls.broker_itau= Broker.objects.create(name='Itau', main_currency=cls.currency_brl, slug='itau')
        cls.broker_inter= Broker.objects.create(name='Inter', main_currency=cls.currency_usd, slug='inter')
        cls.broker_degiro= Broker.objects.create(name='Degiro', main_currency=cls.currency_eur, slug='degiro')
        cls.broker_saxo= Broker.objects.create(name='Saxo', main_currency=cls.currency_eur, slug='saxo')
        cls.category = Category.objects.create(name='Test Category')
        cls.subcategory = SubCategory.objects.create(name='Test SubCategory')
        cls.asset_brl = CurrencyHolding.objects.create(ticker='BRL', category=cls.category, subcategory=cls.subcategory, currency=cls.currency_brl, price_brl=1, price_usd=0.20)
        cls.asset_usd = CurrencyHolding.objects.create(ticker='USD', category=cls.category, subcategory=cls.subcategory, currency=cls.currency_usd, price_brl=5, price_usd=1)
        cls.asset_eur = CurrencyHolding.objects.create(ticker='EUR', category=cls.category, subcategory=cls.subcategory, currency=cls.currency_eur, price_brl=6, price_usd=1.2)
        cls.asset_wege3 = BrStocks.objects.create(ticker='WEGE3', category=cls.category, subcategory=cls.subcategory, price_brl=50, price_usd=10)
        cls.asset_itub4 = BrStocks.objects.create(ticker='ITUB4', category=cls.category, subcategory=cls.subcategory, price_brl=30, price_usd=6)
        cls.asset_msft = Stocks.objects.create(ticker='MSFT', category=cls.category, subcategory=cls.subcategory, price_brl=200, price_usd=40)
        cls.asset_o = Reit.objects.create(ticker='O', category=cls.category, subcategory=cls.subcategory, price_brl=100, price_usd=20)
        cls.user = User.objects.create_user(username='testuser', password='12345')
        cls.portfolio = Portfolio.objects.create(name='Test Portfolio', owner=cls.user)
