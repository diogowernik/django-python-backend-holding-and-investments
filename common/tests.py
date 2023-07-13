from portfolios.models import Portfolio
from investments.models import CurrencyHolding, Stocks, BrStocks, Reit
from brokers.models import Broker
from categories.models import Category, SubCategory
from django.contrib.auth.models import User
from django.utils import timezone
from timewarp.models import CurrencyHistoricalPrice, AssetHistoricalPrice
from common.models import Currency

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
        yesterday = timezone.now() - timezone.timedelta(days=1)
        CurrencyHistoricalPrice.objects.create(currency_pair='BRLUSD', date=yesterday, open=0.18, high=0.18, low=0.18, close=0.18)
        CurrencyHistoricalPrice.objects.create(currency_pair='USDBRL', date=yesterday, open=5.5, high=5.5, low=5.5, close=5.5)
        CurrencyHistoricalPrice.objects.create(currency_pair='USDEUR', date=yesterday, open=0.85, high=0.85, low=0.85, close=0.85)
        CurrencyHistoricalPrice.objects.create(currency_pair='EURUSD', date=yesterday, open=1.15, high=1.15, low=1.15, close=1.15)
        CurrencyHistoricalPrice.objects.create(currency_pair='BRLEUR', date=yesterday, open=0.15, high=0.15, low=0.15, close=0.15)
        CurrencyHistoricalPrice.objects.create(currency_pair='EURBRL', date=yesterday, open=6.5, high=6.5, low=6.5, close=6.5)
        AssetHistoricalPrice.objects.create(asset=cls.asset_wege3, date=yesterday, open=50.5, high=50.5, low=50.5, close=50.5, currency='BRL')
        AssetHistoricalPrice.objects.create(asset=cls.asset_itub4, date=yesterday, open=30.5, high=30.5, low=30.5, close=30.5, currency='BRL')
        AssetHistoricalPrice.objects.create(asset=cls.asset_msft, date=yesterday, open=200.5, high=200.5, low=200.5, close=200.5, currency='USD')
        AssetHistoricalPrice.objects.create(asset=cls.asset_o, date=yesterday, open=100.5, high=100.5, low=100.5, close=100.5, currency='USD')


