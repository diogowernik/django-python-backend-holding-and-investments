from django.test import TestCase
from portfolios.models import Portfolio, PortfolioInvestment, PortfolioTrade
from categories.models import Category, SubCategory
from investments.models import Asset
from brokers.models import Broker
from django.contrib.auth.models import User

# Testes de Trade em BRL
class TradeTestCase(TestCase):
    def setUp(self):
        # Configuração inicial. Criamos os objetos necessários para os testes.
        self.category = Category.objects.create(name='Test Category')
        self.subcategory = SubCategory.objects.create(name='Test SubCategory')
        self.asset_brl = Asset.objects.create(ticker='BRL', category=self.category, subcategory=self.subcategory)
        self.asset_usd = Asset.objects.create(ticker='USD', category=self.category, subcategory=self.subcategory)
        self.asset_wege = Asset.objects.create(ticker='WEGE3', category=self.category, subcategory=self.subcategory)
        self.asset_msft = Asset.objects.create(ticker='MSFT', category=self.category, subcategory=self.subcategory)

        # Cria um usuário para ser o proprietário do portfolio
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Cria um broker para ser usado nas trades
        self.broker = Broker.objects.create(name='Test Broker')

        self.portfolio = Portfolio.objects.create(name='Test Portfolio', owner=self.user)

        # Primeiro, compramos BRL 1000
        self.trade_brl = PortfolioTrade.objects.create(
            order='C',
            asset=self.asset_brl.ticker,
            category='Currency',
            shares_amount=1000.00,
            share_cost_brl=1.00,
            share_cost_usd=0.20,
            broker=self.broker,
            portfolio=self.portfolio,
            usd_on_date=5.00
        )

        # Em seguida, compramos 10 WEGE3
        self.trade_wege = PortfolioTrade.objects.create(
            order='C',
            asset=self.asset_wege.ticker,
            category='Ação',
            shares_amount=10,
            share_cost_brl=36.60,
            share_cost_usd=7.32,
            broker=self.broker,
            portfolio=self.portfolio,
            usd_on_date=5.00
        )

# Teste 1
class BuyBrlTestCase(TradeTestCase):
    def test_balance_after_buy(self):
        # A quantidade cotas de BRL deve ser igual a quantidade de BRL comprada menos o valor da compra de WEGE3
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_brl).shares_amount, 634.00)  # 1000 - 366
        # A quantidade cotas de WEGE3 deve ser igual a quantidade de WEGE3 comprada, pois não havia nenhuma cota anteriormente
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_wege).shares_amount, 10)
        # O preço médio de compra de WEGE3 deve ser igual ao preço de compra, pois não havia nenhuma cota anteriormente para calcular a média
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_wege).share_average_price_brl, 36.60)
        # O preço médio de compra de WEGE3 em USD deve ser igual ao preço de compra, pois não havia nenhuma cota anteriormente para calcular a média
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_wege).share_average_price_usd, 7.32)

# Teste 2
class SellBrlTestCase(TradeTestCase):
    def setUp(self):
        super().setUp()

        self.trade_wege_sell = PortfolioTrade.objects.create(
            order='S',
            asset=self.asset_wege.ticker,
            category='Ação',
            shares_amount=5,
            share_cost_brl=40,
            share_cost_usd=8,
            broker=self.broker,
            portfolio=self.portfolio,
            usd_on_date=5.00
        )

    def test_balance_after_sell(self):
        # A quantidade cotas de BRL deve ser igual a quantidade de BRL comprada menos o valor da compra de WEGE3 mais o valor da venda de WEGE3
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_brl).shares_amount, 834.00) # (1000 - 366) + 200
        # A quantidade cotas de WEGE3 deve ser igual a quantidade de WEGE3 comprada menos a quantidade vendida
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_wege).shares_amount, 5)
        # O preço médio de compra de WEGE3 deve ser igual ao preço anterior, pois a venda não altera o preço médio
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_wege).share_average_price_brl, 36.60)
        # O preço médio de compra de WEGE3 em USD deve ser igual ao preço anterior, pois a venda não altera o preço médio
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_wege).share_average_price_usd, 7.32)

# Teste 3
class AveragePriceUpdateTestCase(TradeTestCase):
    def setUp(self):
        super().setUp()

        # Neste cenário, compramos mais 10 ações da WEGE3 por um preço maior
        self.trade_wege_extra = PortfolioTrade.objects.create(
            order='C',
            asset=self.asset_wege.ticker,
            category='Ação',
            shares_amount=10,
            share_cost_brl=40.00,  # preço maior que o anterior
            share_cost_usd=8.00,  # preço maior que o anterior
            broker=self.broker,
            portfolio=self.portfolio,
            usd_on_date=5.00
        )

    def test_average_price_after_buy(self):
        # A quantidade cotas de WEGE3 deve ser igual a soma das quantidades compradas
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_wege).shares_amount, 20)
        # O preço médio de compra de WEGE3 deve ser a média dos preços de compra, levando em consideração a quantidade comprada em cada preço
        # ((10 * 36.60) + (10 * 40.00)) / 20 = 38.30
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_wege).share_average_price_brl, 38.30)
        # O preço médio de compra de WEGE3 em USD deve ser a média dos preços de compra, levando em consideração a quantidade comprada em cada preço
        # ((10 * 7.32) + (10 * 8.00)) / 20 = 7.66
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_wege).share_average_price_usd, 7.66)

# Testes de Trade com USD
class USDTradeTestCase(TestCase):
    def setUp(self):
        # Configuração inicial. Criamos os objetos necessários para os testes.
        self.category = Category.objects.create(name='Test Category')
        self.subcategory = SubCategory.objects.create(name='Test SubCategory')
        self.asset_usd = Asset.objects.create(ticker='USD', category=self.category, subcategory=self.subcategory)
        self.asset_msft = Asset.objects.create(ticker='MSFT', category=self.category, subcategory=self.subcategory)

        # Cria um usuário para ser o proprietário do portfolio
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Cria um broker para ser usado nas trades, configurado para usar USD como moeda principal
        self.broker = Broker.objects.create(name='Test Broker', main_currency='USD')

        self.portfolio = Portfolio.objects.create(name='Test Portfolio', owner=self.user)

        # Primeiro, compramos USD 1000
        self.trade_usd = PortfolioTrade.objects.create(
            order='C',
            asset=self.asset_usd.ticker,
            category='Currency',
            shares_amount=1000.00,
            share_cost_brl=5.00,
            share_cost_usd=1.00,
            broker=self.broker,
            portfolio=self.portfolio,
            usd_on_date=5.00
        )

        # Em seguida, compramos 10 MSFT
        self.trade_msft = PortfolioTrade.objects.create(
            order='C',
            asset=self.asset_msft.ticker,
            category='Ação',
            shares_amount=10,
            share_cost_brl=200.00,
            share_cost_usd=40.00,
            broker=self.broker,
            portfolio=self.portfolio,
            usd_on_date=5.00
        )

# Teste 4
class BuyUsdTestCase(USDTradeTestCase):
    def test_balance_after_buy(self):
        # A quantidade de cotas de USD deve ser igual à quantidade de USD comprado menos o valor da compra de MSFT
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_usd).shares_amount, 600.00)  # 1000 - 400
        # A quantidade de cotas de MSFT deve ser igual à quantidade de MSFT comprada, pois não havia nenhuma cota anteriormente
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_msft).shares_amount, 10)
        # O preço médio de compra de MSFT deve ser igual ao preço de compra, pois não havia nenhuma cota anteriormente para calcular a média
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_msft).share_average_price_brl, 200.00)
        # O preço médio de compra de MSFT em USD deve ser igual ao preço de compra, pois não havia nenhuma cota anteriormente para calcular a média
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_msft).share_average_price_usd, 40.00)

# Teste 5
class SellUsdTestCase(USDTradeTestCase):
    def setUp(self):
        super().setUp()

        self.trade_msft_sell = PortfolioTrade.objects.create(
            order='S',
            asset=self.asset_msft.ticker,
            category='Ação',
            shares_amount=5,
            share_cost_brl=220.00,
            share_cost_usd=44.00,
            broker=self.broker,
            portfolio=self.portfolio,
            usd_on_date=5.00
        )

    def test_balance_after_sell(self):
        # A quantidade de cotas de USD deve ser igual à quantidade de USD comprado menos o valor da compra de MSFT mais o valor da venda de MSFT
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_usd).shares_amount, 820.00)  # (1000 - 400) + 220
        # A quantidade de cotas de MSFT deve ser igual à quantidade de MSFT comprada menos a quantidade vendida
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_msft).shares_amount, 5)
        # O preço médio de compra de MSFT deve ser igual ao preço anterior, pois a venda não altera o preço médio
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_msft).share_average_price_brl, 200.00)
        # O preço médio de compra de MSFT em USD deve ser igual ao preço anterior, pois a venda não altera o preço médio
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_msft).share_average_price_usd, 40.00)

# Teste 6
class UsdAveragePriceUpdateTestCase(USDTradeTestCase):
    def setUp(self):
        super().setUp()

        # Neste cenário, compramos mais 10 ações da MSFT por um preço maior
        self.trade_msft_extra = PortfolioTrade.objects.create(
            order='C',
            asset=self.asset_msft.ticker,
            category='Ação',
            shares_amount=10,
            share_cost_brl=220.00,  # preço maior que o anterior
            share_cost_usd=44.00,  # preço maior que o anterior
            broker=self.broker,
            portfolio=self.portfolio,
            usd_on_date=5.00
        )

    def test_average_price_after_buy(self):
        # A quantidade de cotas de MSFT deve ser igual à soma das quantidades compradas
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_msft).shares_amount, 20)
        # O preço médio de compra de MSFT deve ser a média dos preços de compra, levando em consideração a quantidade comprada em cada preço
        # ((10 * 200.00) + (10 * 220.00)) / 20 = 210.00
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_msft).share_average_price_brl, 210.00)
        # O preço médio de compra de MSFT em USD deve ser a média dos preços de compra, levando em consideração a quantidade comprada em cada preço
        # ((10 * 40.00) + (10 * 44.00)) / 20 = 42.00
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, asset=self.asset_msft).share_average_price_usd, 42.00)

# Teste 7
class MultiBrokerBrlTestCase(TradeTestCase):
    def setUp(self):
        super().setUp()

        # Cria duas novas corretoras para serem usadas nas transações
        self.broker1_new = Broker.objects.create(name='Test Broker 1 New', slug='test-broker-1-new')
        self.broker2_new = Broker.objects.create(name='Test Broker 2 New', slug='test-broker-2-new')

        # Compramos BRL 1000 na primeira nova corretora
        self.trade_brl_broker1_new = PortfolioTrade.objects.create(
            order='C',
            asset=self.asset_brl.ticker,
            category='Currency',
            shares_amount=1000.00,
            share_cost_brl=1.00,
            share_cost_usd=0.20,
            broker=self.broker1_new,
            portfolio=self.portfolio,
            usd_on_date=5.00
        )

        # Compramos BRL 2000 na segunda nova corretora
        self.trade_brl_broker2_new = PortfolioTrade.objects.create(
            order='C',
            asset=self.asset_brl.ticker,
            category='Currency',
            shares_amount=2000.00,
            share_cost_brl=1.00,
            share_cost_usd=0.20,
            broker=self.broker2_new,
            portfolio=self.portfolio,
            usd_on_date=5.00
        )

    def test_balance_after_buy(self):
        # A quantidade de cotas de BRL na nova corretora 1 deve ser igual à quantidade de BRL comprada na nova corretora 1
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, broker=self.broker1_new, asset=self.asset_brl).shares_amount, 1000.00)
        # A quantidade de cotas de BRL na nova corretora 2 deve ser igual à quantidade de BRL comprada na nova corretora 2
        self.assertEqual(PortfolioInvestment.objects.get(portfolio=self.portfolio, broker=self.broker2_new, asset=self.asset_brl).shares_amount, 2000.00)
