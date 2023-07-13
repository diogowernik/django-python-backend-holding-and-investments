from django.test import TestCase
from portfolios.models import PortfolioInvestment
from cashflow.models import CurrencyTransaction
from django.utils import timezone
from common.tests import CommonSetupMixin # criado por mim para facilitar a criação de objetos para testes
from trade.models import Trade, TradeCalculation, TradeHistory

class TradeTest(CommonSetupMixin, TestCase):
    def create_asset_transaction(self, amount, price_brl, price_usd, transaction_type='buy', asset=None, broker=None):
        # Método auxiliar para criar transações de ativos.
        return Trade.objects.create(portfolio=self.portfolio, broker=broker or self.broker_banco_brasil, transaction_type=transaction_type, asset=asset, transaction_amount=amount, price_brl=price_brl, price_usd=price_usd)
    
    def test_brl_banco_do_brasil_asset_buy(self):
        transaction1 = self.create_asset_transaction(100, 10, 2, 'buy', self.asset_wege3, self.broker_banco_brasil)
        transaction2 = self.create_asset_transaction(200, 20, 4, 'buy', self.asset_wege3, self.broker_banco_brasil)
        transaction3 = self.create_asset_transaction(300, 30, 6, 'buy', self.asset_wege3, self.broker_banco_brasil)

        # verifica se o portfolio investment foi criado corretamente
        portfolio_investment = PortfolioInvestment.objects.get(id=transaction3.portfolio_investment.id)
        self.assertEqual(portfolio_investment.portfolio, self.portfolio)

        # verifica se as shares amount estão corretas
        self.assertEqual(portfolio_investment.shares_amount, 600)

        # verifica se o preço total está correto
        # total_cost_brl = 1000 + 4000 + 9000 = 14000
        self.assertEqual(portfolio_investment.total_cost_brl, 14000)
        # total_cost_usd = 200 + 800 + 1800 = 2800
        self.assertEqual(portfolio_investment.total_cost_usd, 2800)

        # verifica se o preço médio está correto
        # average_price_brl = 14000 / 600 = 23.33
        self.assertEqual(portfolio_investment.share_average_price_brl, 23.333333333333332)
        # average_price_usd = 2800 / 600 = 4.66
        self.assertEqual(portfolio_investment.share_average_price_usd, 4.666666666666667)

        # verifica se foi criada uma nova CurrencyTransaction
        # Check if a new CurrencyTransaction was created
        currency_transactions = CurrencyTransaction.objects.filter(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_date=transaction3.transaction_date)
        self.assertEqual(len(currency_transactions), 1)

        # Check the CurrencyTransaction details
        currency_transaction = currency_transactions[0]
        self.assertEqual(currency_transaction.transaction_type, 'withdraw')
        self.assertEqual(currency_transaction.transaction_amount, transaction3.transaction_amount * transaction3.price_brl)

    def test_brl_banco_do_brasil_asset_sell(self):
        transaction1 = Trade.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=100, price_brl=10, price_usd=2)
        transaction2 = Trade.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=200, price_brl=20, price_usd=4)
        transaction3 = Trade.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=300, price_brl=30, price_usd=6)
        transaction4 = Trade.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='sell', asset=self.asset_wege3, transaction_amount=400, price_brl=40, price_usd=8)

        # verifica se o portfolio investment foi criado corretamente
        portfolio_investment = PortfolioInvestment.objects.get(id=transaction4.portfolio_investment.id)
        self.assertIsNotNone(portfolio_investment)

        # verifica se as shares amount estão corretas
        self.assertEqual(portfolio_investment.shares_amount, 200) # 100 + 200 + 300 - 400

        # verifica se o custo total está correto
        self.assertAlmostEqual(portfolio_investment.total_cost_brl, 200 * 23.33333333333334, delta=0.01)  

        # verifica se o preço médio está correto
        self.assertEqual(portfolio_investment.share_average_price_brl, 23.33333333333334)  # 6000 BRL / 200 shares

        # verifica se o lucro/prejuizo está correto
        profit_brl = 400 * (40 - 23.33333333333334)
        self.assertAlmostEqual(portfolio_investment.trade_profit_brl, profit_brl, delta=0.01)

        # verifica se foi criada uma nova CurrencyTransaction
        currency_transaction = CurrencyTransaction.objects.filter(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_date=transaction4.transaction_date).first()
        self.assertIsNotNone(currency_transaction)

        # verifica se a transaction_amount está correta
        self.assertEqual(currency_transaction.transaction_amount, 400*40)  # 400 shares at 40 BRL each

    def test_brl_banco_do_brasil_asset_delete(self):
        transaction1 = Trade.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=100, price_brl=10, price_usd=2)
        transaction2 = Trade.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=200, price_brl=20, price_usd=4)
        transaction3 = Trade.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=300, price_brl=30, price_usd=6)

        # Deleta a segunda transação
        transaction2_id = transaction2.id
        transaction2.delete()

        # Verifica se a transação foi deletada corretamente
        with self.assertRaises(Trade.DoesNotExist):
            Trade.objects.get(id=transaction2_id)

        # Verifica se o portfolio investment foi atualizado corretamente
        portfolio_investment = PortfolioInvestment.objects.get(id=transaction3.portfolio_investment.id)
        self.assertEqual(portfolio_investment.shares_amount, 400)  # 100 + 300
        self.assertEqual(portfolio_investment.total_cost_brl, 10000)  # 1000 + 9000
        self.assertEqual(portfolio_investment.share_average_price_brl, 25)  # 10000 / 400

        # Verifica se a CurrencyTransaction correspondente à transação deletada também foi deletada
        currency_transactions = CurrencyTransaction.objects.filter(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_date=transaction2.transaction_date)
        self.assertEqual(len(currency_transactions), 0)

    def test_brl_broker_diff_asset_no_delete(self):
        transaction1 = Trade.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=100, price_brl=10, price_usd=2)
        transaction2 = Trade.objects.create(portfolio=self.portfolio, broker=self.broker_itau, transaction_type='buy', asset=self.asset_wege3, transaction_amount=200, price_brl=20, price_usd=4)
        transaction3 = Trade.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=300, price_brl=30, price_usd=6)

        # Verifica se o portfolio investment do broker_banco_brasil foi atualizado corretamente
        portfolio_investment_banco_brasil = PortfolioInvestment.objects.get(broker=self.broker_banco_brasil, asset=self.asset_wege3)
        self.assertEqual(portfolio_investment_banco_brasil.shares_amount, 400)  # 100 + 300
        self.assertEqual(portfolio_investment_banco_brasil.total_cost_brl, 10000)  # 1000 + 9000
        self.assertEqual(portfolio_investment_banco_brasil.share_average_price_brl, 25)  # 10000 / 400

        # Verifica se o portfolio investment do broker_itau foi criado corretamente
        portfolio_investment_itau = PortfolioInvestment.objects.get(broker=self.broker_itau, asset=self.asset_wege3)
        self.assertEqual(portfolio_investment_itau.shares_amount, 200)  # 200
        self.assertEqual(portfolio_investment_itau.total_cost_brl, 4000)  # 200 * 20
        self.assertEqual(portfolio_investment_itau.share_average_price_brl, 20)  # 4000 / 200

        # Verifica se a CurrencyTransaction correspondente à transação no broker itau foi criada
        currency_transactions = CurrencyTransaction.objects.filter(portfolio=self.portfolio, broker=self.broker_itau, transaction_date=transaction2.transaction_date)
        self.assertEqual(len(currency_transactions), 1)
        
        # Verifica os detalhes da CurrencyTransaction
        currency_transaction = currency_transactions[0]
        self.assertEqual(currency_transaction.transaction_type, 'withdraw')
        self.assertEqual(currency_transaction.transaction_amount, transaction2.transaction_amount * transaction2.price_brl)

    def test_brl_same_broker_edit_transaction(self):
        transaction1 = Trade.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=100, price_brl=10, price_usd=2)
        transaction2 = Trade.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=200, price_brl=20, price_usd=4)
        transaction3 = Trade.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=300, price_brl=30, price_usd=6)

        # Edit the second transaction
        transaction2.transaction_amount = 150
        transaction2.price_brl = 15
        transaction2.price_usd = 3
        transaction2.save()

        # Check if the portfolio investment was updated correctly
        portfolio_investment = PortfolioInvestment.objects.get(id=transaction3.portfolio_investment.id)
        self.assertEqual(portfolio_investment.shares_amount, 550)  # 100 + 150 + 300
        self.assertEqual(portfolio_investment.total_cost_brl, 12250)  # 1000 + 2250 + 9000
        self.assertEqual(portfolio_investment.share_average_price_brl, 22.272727272727273)  # 12250 / 550

        # Check if the corresponding CurrencyTransaction was also updated
        currency_transactions = CurrencyTransaction.objects.filter(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_date=transaction2.transaction_date)
        self.assertEqual(len(currency_transactions), 1)

        # Check the CurrencyTransaction details
        currency_transaction = currency_transactions[0]
        self.assertEqual(currency_transaction.transaction_type, 'withdraw')
        self.assertEqual(currency_transaction.transaction_amount, transaction2.transaction_amount * transaction2.price_brl)


class AssetPriceTestCase(CommonSetupMixin, TestCase):
    def setUp(self):
        super().setUp() # calling the setup of CommonSetupMixin

    def create_transaction_no_price(self, asset, amount, broker=None, transaction_date=None):
        # Helper method to create transactions without a defined price.
        return Trade.objects.create(asset=asset, portfolio=self.portfolio, broker=broker or self.broker_banco_brasil, transaction_amount=amount, transaction_date=transaction_date or timezone.now())

    def test_set_prices_brl_banco_brasil(self):
        # Test to check if the set_prices method is working correctly for BRL
        yesterday = timezone.now() - timezone.timedelta(days=1)
        transaction = self.create_transaction_no_price(self.asset_wege3, 1000, broker=self.broker_banco_brasil, transaction_date=yesterday)
        self.assertEqual(transaction.price_brl, 50.5) # Obtained from historical data
        self.assertEqual(transaction.price_usd, 50.5 * 0.18)  # Converted from BRL to USD using historical data

    def test_set_prices_usd_avenue(self):
        # Test to check if the set_prices method is working correctly for USD
        yesterday = timezone.now() - timezone.timedelta(days=1)
        transaction = self.create_transaction_no_price(self.asset_msft, 1000, broker=self.broker_avenue, transaction_date=yesterday)
        self.assertEqual(transaction.price_brl, 200.5 * 5.5)  # Converted from USD to BRL using historical data
        self.assertEqual(transaction.price_usd, 200.5) # Obtained from historical data

    def test_set_prices_brl_banco_brasil_today(self):
        # Test to check if the set_prices method is working correctly for BRL with today's date
        transaction = self.create_transaction_no_price(self.asset_wege3, 1000, broker=self.broker_banco_brasil)
        self.assertEqual(transaction.price_brl, self.asset_wege3.price_brl) # Obtained from the asset's current price
        self.assertEqual(transaction.price_usd, self.asset_wege3.price_usd) # Obtained from the asset's current price

    def test_set_prices_usd_avenue_today(self):
        # Test to check if the set_prices method is working correctly for USD with today's date
        transaction = self.create_transaction_no_price(self.asset_msft, 1000, broker=self.broker_avenue)
        self.assertEqual(transaction.price_brl, self.asset_msft.price_brl) # Obtained from the asset's current price
        self.assertEqual(transaction.price_usd, self.asset_msft.price_usd) # Obtained from the asset's current price

# teste valores na criação de historico != valores para atualização de portfolio investment
# teste quando cria um historico, se é criado um portfolio dividend