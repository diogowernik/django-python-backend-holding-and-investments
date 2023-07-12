from django.test import TestCase
from cashflow.models import AssetTransaction, TransactionsHistory
from portfolios.models import PortfolioInvestment
from dividends.models import Dividend, PortfolioDividend
from django.utils import timezone
from common.tests import CommonSetupMixin

class DividendsTestCase(CommonSetupMixin, TestCase):
    def setUp(self):
        super().setUp()  # Calling the setup of CommonSetupMixin
        self.create_asset_transaction('buy', self.asset_itub4, 100, 90)
        self.create_asset_transaction('buy', self.asset_itub4, 100, 60)
        self.create_asset_transaction('sell', self.asset_itub4, 100, 30)

    def create_asset_transaction(self, transaction_type, asset, amount, days_ago):
        return AssetTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type=transaction_type, asset=asset, transaction_amount=amount, price_brl=30, price_usd=6, transaction_date=timezone.now() - timezone.timedelta(days=days_ago))

    def create_dividend(self, asset, value_per_share_brl, value_per_share_usd, record_days_ago, pay_days_ago):
        return Dividend.objects.create(asset=asset, value_per_share_brl=value_per_share_brl, value_per_share_usd=value_per_share_usd, record_date=(timezone.now() - timezone.timedelta(days=record_days_ago)), pay_date=(timezone.now() - timezone.timedelta(days=pay_days_ago)))

    def test_create_dividends(self):
        # Creating a dividend
        dividend = self.create_dividend(self.asset_itub4, 2, 0.4, 20, 10)

        # More than one portfolio_dividend can be created for the same dividend
        portfolio_dividends = list(PortfolioDividend.objects.filter(dividend=dividend))
        self.assertTrue(portfolio_dividends)  # checks if the list is not empty

        for portfolio_dividend in portfolio_dividends:
            # Check if PortfolioDividends have correct values
            self.assertAlmostEqual(portfolio_dividend.value_per_share_brl, 2)
            self.assertAlmostEqual(portfolio_dividend.value_per_share_usd, 0.4)
            self.assertEqual(portfolio_dividend.pay_date, dividend.pay_date)
            self.assertEqual(portfolio_dividend.shares_amount, 100)  # as it is 20 days ago, 100 + 100 - 100 = 100

    def test_create_dividends_40_days_ago(self):
        # Creating a dividend
        dividend = self.create_dividend(self.asset_itub4, 2, 0.4, 40, 10)

        # More than one portfolio_dividend can be created for the same dividend
        # Find all portfolio_dividends that were created for the added dividend.
        portfolio_dividends = list(PortfolioDividend.objects.filter(dividend=dividend))
        self.assertTrue(portfolio_dividends)  # checks if the list is not empty

        for portfolio_dividend in portfolio_dividends:
            # Check if PortfolioDividends have correct values
            self.assertAlmostEqual(portfolio_dividend.value_per_share_brl, 2)
            self.assertAlmostEqual(portfolio_dividend.value_per_share_usd, 0.4)
            self.assertEqual(portfolio_dividend.pay_date, dividend.pay_date)
            self.assertEqual(portfolio_dividend.shares_amount, 200)  # as it is 40 days ago, 100 + 100 = 200

    def test_create_multiple_dividends_for_same_asset(self):
        dividend1 = self.create_dividend(self.asset_itub4, 2, 0.4, 40, 10)
        dividend2 = self.create_dividend(self.asset_itub4, 2, 0.4, 30, 10)
        portfolio_dividends = list(PortfolioDividend.objects.filter(asset=self.asset_itub4))
        self.assertEqual(len(portfolio_dividends), 2)
    
    def test_create_dividends_with_zero_shares(self):
        self.create_asset_transaction('sell', self.asset_itub4, 200, 10)  # Selling all shares
        dividend = self.create_dividend(self.asset_itub4, 2, 0.4, 5, 1)  # Creating a dividend after selling all shares
        # Quando a quantidade de ações é 0, a instância PortfolioDividend não deve ser criada
        portfolio_dividend = PortfolioDividend.objects.filter(dividend=dividend).first()
        self.assertIsNone(portfolio_dividend)

    def test_delete_dividend(self):
        dividend = self.create_dividend(self.asset_itub4, 2, 0.4, 40, 10)
        dividend_id = dividend.id
        dividend.delete()
        portfolio_dividends = PortfolioDividend.objects.filter(dividend__id=dividend_id)
        self.assertFalse(portfolio_dividends.exists())

    def test_update_dividend(self):
        dividend = self.create_dividend(self.asset_itub4, 2, 0.4, 40, 10)
        portfolio_dividend_original = PortfolioDividend.objects.filter(dividend=dividend).first()
        
        dividend.value_per_share_brl = 3
        dividend.value_per_share_usd = 0.5
        dividend.save()
        
        portfolio_dividend_updated = PortfolioDividend.objects.filter(dividend=dividend).first()
        self.assertNotEqual(portfolio_dividend_original.value_per_share_brl, portfolio_dividend_updated.value_per_share_brl)
        self.assertNotEqual(portfolio_dividend_original.value_per_share_usd, portfolio_dividend_updated.value_per_share_usd)


class PortfolioDividendTest(CommonSetupMixin, TestCase):
    def test_asset_transaction_before_dividend(self):
        # Primeiro, criamos um Dividend em um dia qualquer.
        dividend_wege = Dividend.objects.create(
            asset=self.asset_wege3, 
            value_per_share_brl=2, 
            value_per_share_usd=0.4, 
            record_date='2020-01-01',
            pay_date='2020-01-02')
        
        # verificamos se o dividendo foi criado corretamente
        self.assertIsNotNone(dividend_wege) # Ok

        # Então, 10 dias depois, criamos uma AssetTransaction com o transaction date antes do record_date do Dividend
        wege_transaction = AssetTransaction.objects.create(
            asset=self.asset_wege3,
            portfolio=self.portfolio,
            broker=self.broker_inter,
            transaction_type='buy',
            transaction_date='2019-12-22',
            transaction_amount=100,
            price_brl=10,
            price_usd=2,
            )
        
        # Verificamos se a AssetTransaction foi criada corretamente
        self.assertIsNotNone(wege_transaction) # Ok

        # Recuperamos a instância TransactionsHistory associada a essa AssetTransaction
        transaction_history = TransactionsHistory.objects.filter(transaction=wege_transaction).first()

        # Verificamos se existe um transaction_history criado para essa AssetTransaction
        self.assertIsNotNone(transaction_history) # Ok

        # Verificamos se existe um PortfolioInvestment criado para essa AssetTransaction
        portfolio_investment = PortfolioInvestment.objects.filter(
            asset=self.asset_wege3,
            portfolio=self.portfolio,
            broker=self.broker_inter,
            ).first()

        # Como a AssetTransaction foi realizada antes da record_date do Dividend, deve haver um PortfolioDividend criado
        self.assertIsNotNone(portfolio_investment) # Ok

        # Verificamos se o PortfolioDividend foi criado corretamente
        portfolio_dividend = PortfolioDividend.objects.filter(
            portfolio_investment=portfolio_investment,
            ).first()
        self.assertIsNotNone(portfolio_dividend)

        # Verificamos se o PortfolioDividend foi criado com os valores corretos
        self.assertEqual(portfolio_dividend.value_per_share_brl, 2)
        self.assertEqual(portfolio_dividend.value_per_share_usd, 0.4)
        self.assertEqual(portfolio_dividend.shares_amount, 100)

    def test_asset_transaction_after_dividend(self):
        # Primeiro, criamos um Dividend em um dia qualquer.
        dividend_wege = Dividend.objects.create(
            asset=self.asset_wege3, 
            value_per_share_brl=2, 
            value_per_share_usd=0.4, 
            record_date='2020-01-01',
            pay_date='2020-01-02')
        
        # verificamos se o dividendo foi criado corretamente
        self.assertIsNotNone(dividend_wege)

        # Então, 10 dias depois, criamos uma AssetTransaction com o transaction date depois do record_date do Dividend
        # Nesse caso, não deve haver um PortfolioDividend criado
        # A AssetTransaction deve ser criada normalmente, mas sem um PortfolioDividend associado
        wege_transaction = AssetTransaction.objects.create(
            asset=self.asset_wege3,
            portfolio=self.portfolio,
            broker=self.broker_inter,
            transaction_type='buy',
            transaction_date='2020-01-12',
            transaction_amount=100,
            price_brl=10,
            price_usd=2,
            )

        # Verificamos se a AssetTransaction foi criada corretamente
        self.assertIsNotNone(wege_transaction) # Ok

        # Recuperamos a instância TransactionsHistory associada a essa AssetTransaction
        transaction_history = TransactionsHistory.objects.filter(transaction=wege_transaction).first()

        self.assertIsNotNone(transaction_history) # Ok

        # Verificamos se existe um PortfolioInvestment criado para essa AssetTransaction
        portfolio_investment = PortfolioInvestment.objects.filter(
            asset=self.asset_wege3,
            portfolio=self.portfolio,
            broker=self.broker_inter,
            ).first()

        # Como a AssetTransaction foi realizada depois da record_date do Dividend, não deve haver um PortfolioDividend criado
        self.assertIsNotNone(portfolio_investment) # Ok

        # Verificamos que não existe um PortfolioDividend criado para essa AssetTransaction
        portfolio_dividend = PortfolioDividend.objects.filter(
            portfolio_investment=portfolio_investment,
            ).first()
        self.assertIsNone(portfolio_dividend)        

    # criar outros testes para situações diferentes, por exemplo, 
    # 2) se editar uma AssetTransaction e mudar o transaction_date, para antes ou depois do record_date do Dividend, vai criar ou apagar um PortfolioDividend?
    # 3) se apagar uma AssetTransaction, vai apagar os PortfolioDividends associado ao HistoryTransaction
    # 4) se apagar uma AssetTransaction, vai apagar o PortfolioDividend associado ao HistoryTransaction, mas se tiver outro HistoryTransaction com mesmos critérios não pode apagar, tem que atualizar.
    
    # se criar 2 Dividends e 1 AssetTransaction antes do record_date dos dois Dividends, deve criar 2 PortfolioDividends.
    def test_multiple_dividends_before_asset_transaction(self):
            # Primeiro, criamos dois Dividends em dias diferentes.
        dividend_wege1 = Dividend.objects.create(
            asset=self.asset_wege3, 
            value_per_share_brl=2, 
            value_per_share_usd=0.4, 
            record_date='2020-01-01',
            pay_date='2020-01-02')

        dividend_wege2 = Dividend.objects.create(
            asset=self.asset_wege3, 
            value_per_share_brl=2, 
            value_per_share_usd=0.4, 
            record_date='2020-02-01',
            pay_date='2020-02-02')

        # verificamos se os dividendos foram criados corretamente
        self.assertIsNotNone(dividend_wege1)
        self.assertIsNotNone(dividend_wege2)

        # Criamos uma AssetTransaction com o transaction date antes do record_date dos dois Dividends
        wege_transaction = AssetTransaction.objects.create(
            asset=self.asset_wege3,
            portfolio=self.portfolio,
            broker=self.broker_inter,
            transaction_type='buy',
            transaction_date='2019-12-22',
            transaction_amount=100,
            price_brl=10,
            price_usd=2,
            )

        # Verificamos se a AssetTransaction foi criada corretamente
        self.assertIsNotNone(wege_transaction) 

        # Recuperamos a instância TransactionsHistory associada a essa AssetTransaction
        transaction_history = TransactionsHistory.objects.filter(transaction=wege_transaction).first()

        # Verificamos se existe um transaction_history criado para essa AssetTransaction
        self.assertIsNotNone(transaction_history)

        # Verificamos se existe um PortfolioInvestment criado para essa AssetTransaction
        portfolio_investment = PortfolioInvestment.objects.filter(
            asset=self.asset_wege3,
            portfolio=self.portfolio,
            broker=self.broker_inter,
            ).first()

        self.assertIsNotNone(portfolio_investment) 

        # Como a AssetTransaction foi realizada antes da record_date dos Dividends, devem existir 2 PortfolioDividends criados
        portfolio_dividends = PortfolioDividend.objects.filter(portfolio_investment=portfolio_investment)
        self.assertEqual(portfolio_dividends.count(), 2)

    # se tiver 2 AsssetTransactions antes do record_date do Dividend, deve criar 1 PortfolioDividend, somando as duas AssetTransactions
    def test_multiple_transactions_before_dividend_single_investment(self):
        # Primeiro, criamos um Dividend em um dia qualquer.
        dividend_wege = Dividend.objects.create(
            asset=self.asset_wege3, 
            value_per_share_brl=2, 
            value_per_share_usd=0.4, 
            record_date='2020-01-01',
            pay_date='2020-01-02')

        # verificamos se o dividendo foi criado corretamente
        self.assertIsNotNone(dividend_wege)

        # Criamos duas AssetTransactions com o transaction date antes do record_date do Dividend
        wege_transaction1 = AssetTransaction.objects.create(
            asset=self.asset_wege3,
            portfolio=self.portfolio,
            broker=self.broker_inter,
            transaction_type='buy',
            transaction_date='2019-12-22',
            transaction_amount=100,
            price_brl=10,
            price_usd=2,
            )

        wege_transaction2 = AssetTransaction.objects.create(
            asset=self.asset_wege3,
            portfolio=self.portfolio,
            broker=self.broker_inter,
            transaction_type='buy',
            transaction_date='2019-12-23',
            transaction_amount=50,
            price_brl=10,
            price_usd=2,
            )

        # Verificamos se as AssetTransactions foram criadas corretamente
        self.assertIsNotNone(wege_transaction1) 
        self.assertIsNotNone(wege_transaction2) 

        # Recuperamos as instâncias TransactionsHistory associadas a essas AssetTransactions
        transaction_history1 = TransactionsHistory.objects.filter(transaction=wege_transaction1).first()
        # verificamos a quantidade de shares_amount do transaction_history1
        self.assertEqual(transaction_history1.total_shares, 100) # OK
        transaction_history2 = TransactionsHistory.objects.filter(transaction=wege_transaction2).first()
        # verificamos a quantidade de shares_amount do transaction_history2
        self.assertEqual(transaction_history2.total_shares, 150) # OK este é que deve valer para este caso

        # Verificamos se existe um PortfolioInvestment criado para essas AssetTransactions
        portfolio_investment = PortfolioInvestment.objects.filter(
            asset=self.asset_wege3,
            portfolio=self.portfolio,
            broker=self.broker_inter,
            ).first()

        self.assertIsNotNone(portfolio_investment) 

        # Verifica se foi criado apenas um PortfolioDividend ou dois
        portfolio_dividends = PortfolioDividend.objects.filter(portfolio_investment=portfolio_investment)
        self.assertEqual(portfolio_dividends.count(), 1)

        # get this PortfolioDividend
        portfolio_dividend = portfolio_dividends.first()

        # Verificamos se o shares_amount do PortfolioDividend é correto
        self.assertEqual(portfolio_dividend.shares_amount, 150)

    # se editar uma AssetTransaction e mudar o numero de transaction_amount, vai mudar o numero de shares_amount do PortfolioDividend?
    def test_edit_asset_transaction_changes_portfolio_dividend(self):
        # Primeiro, criamos um Dividend em um dia qualquer.
        dividend_wege = Dividend.objects.create(
            asset=self.asset_wege3, 
            value_per_share_brl=2, 
            value_per_share_usd=0.4, 
            record_date='2020-01-01',
            pay_date='2020-01-02')

        # verificamos se o dividendo foi criado corretamente
        self.assertIsNotNone(dividend_wege)

        # Criamos uma AssetTransaction com o transaction date antes do record_date do Dividend
        wege_transaction = AssetTransaction.objects.create(
            asset=self.asset_wege3,
            portfolio=self.portfolio,
            broker=self.broker_inter,
            transaction_type='buy',
            transaction_date='2019-12-22',
            transaction_amount=100,
            price_brl=10,
            price_usd=2,
            )

        # Verificamos se a AssetTransaction foi criada corretamente
        self.assertIsNotNone(wege_transaction) 

        # Recuperamos a instância TransactionsHistory associada a essa AssetTransaction
        transaction_history = TransactionsHistory.objects.filter(transaction=wege_transaction).first()

        # Verificamos se existe um transaction_history criado para essa AssetTransaction
        self.assertIsNotNone(transaction_history)

        # verificamos se o total_shares do transaction_history é correto
        self.assertEqual(transaction_history.total_shares, 100)

        # Editamos o transaction_amount da AssetTransaction
        wege_transaction.transaction_amount = 200
        wege_transaction.save()

        # Verificamos se o total_shares do transaction_history foi atualizado corretamente
        transaction_history.refresh_from_db()
        self.assertEqual(transaction_history.total_shares, 200)

        # Verificamos se existe um PortfolioInvestment criado para essa AssetTransaction
        portfolio_investment = PortfolioInvestment.objects.filter(
            asset=self.asset_wege3,
            portfolio=self.portfolio,
            broker=self.broker_inter,
            ).first()

        self.assertIsNotNone(portfolio_investment) 

        # Verificamos se o PortfolioDividend foi criado corretamente
        portfolio_dividend = PortfolioDividend.objects.filter(
            portfolio_investment=portfolio_investment,
            ).first()
        self.assertIsNotNone(portfolio_dividend)

        # Verificamos se o shares_amount do PortfolioDividend mudou conforme esperado
        self.assertEqual(portfolio_dividend.shares_amount, 200)

    def test_single_transactions_before_dividend_and_delete_transaction(self):
            # Primeiro, criamos um Dividend em um dia qualquer.
        dividend_wege = Dividend.objects.create(
            asset=self.asset_wege3, 
            value_per_share_brl=2, 
            value_per_share_usd=0.4, 
            record_date='2020-01-01',
            pay_date='2020-01-02')

        # verificamos se o dividendo foi criado corretamente
        self.assertIsNotNone(dividend_wege)

        # Criamos duas AssetTransactions com o transaction date antes do record_date do Dividend
        wege_transaction1 = AssetTransaction.objects.create(
            asset=self.asset_wege3,
            portfolio=self.portfolio,
            broker=self.broker_inter,
            transaction_type='buy',
            transaction_date='2019-12-22',
            transaction_amount=100,
            price_brl=10,
            price_usd=2,
            )

        # Verificamos se as AssetTransactions foram criadas corretamente
        self.assertIsNotNone(wege_transaction1) 

        # Recuperamos as instâncias TransactionsHistory associadas a essas AssetTransactions
        transaction_history1 = TransactionsHistory.objects.filter(transaction=wege_transaction1).first()
        # verificamos a quantidade de shares_amount do transaction_history1
        self.assertEqual(transaction_history1.total_shares, 100) # OK

        # delete wege_transaction2
        wege_transaction1.delete()
        
        # Verificamos se o transaction_history2 foi apagado
        transaction_history1 = TransactionsHistory.objects.filter(transaction=wege_transaction1).first()
        self.assertIsNone(transaction_history1)

        # Verificamos se existe um PortfolioInvestment criado para essas AssetTransactions
        portfolio_investment = PortfolioInvestment.objects.filter(
            asset=self.asset_wege3,
            portfolio=self.portfolio,
            broker=self.broker_inter,
            ).first()

        self.assertIsNotNone(portfolio_investment) 

        # Verifica se foi o PortfolioDividend foi apagado
        portfolio_dividends = PortfolioDividend.objects.filter(portfolio_investment=portfolio_investment)
        self.assertEqual(portfolio_dividends.count(), 0)
        
    #se apagar uma AssetTransaction, vai apagar o PortfolioDividend associado ao HistoryTransaction, 
    # mas se tiver outro HistoryTransaction, não apaga o PortfolioDividend mas atualiza ele.
    def test_multiple_transactions_before_dividend_single_dividend_delete_one(self):
        # Primeiro, criamos um Dividend em um dia qualquer.
        dividend_wege = Dividend.objects.create(
            asset=self.asset_wege3, 
            value_per_share_brl=2, 
            value_per_share_usd=0.4, 
            record_date='2020-01-01',
            pay_date='2020-01-02')

        # verificamos se o dividendo foi criado corretamente
        self.assertIsNotNone(dividend_wege)

        # Criamos duas AssetTransactions com o transaction date antes do record_date do Dividend
        wege_transaction1 = AssetTransaction.objects.create(
            asset=self.asset_wege3,
            portfolio=self.portfolio,
            broker=self.broker_inter,
            transaction_type='buy',
            transaction_date='2019-12-22',
            transaction_amount=100,
            price_brl=10,
            price_usd=2,
            )

        wege_transaction2 = AssetTransaction.objects.create(
            asset=self.asset_wege3,
            portfolio=self.portfolio,
            broker=self.broker_inter,
            transaction_type='buy',
            transaction_date='2019-12-23',
            transaction_amount=50,
            price_brl=10,
            price_usd=2,
            )

        # Verificamos se as AssetTransactions foram criadas corretamente
        self.assertIsNotNone(wege_transaction1) 
        self.assertIsNotNone(wege_transaction2) 

        # Recuperamos as instâncias TransactionsHistory associadas a essas AssetTransactions
        transaction_history1 = TransactionsHistory.objects.filter(transaction=wege_transaction1).first()
        # verificamos a quantidade de shares_amount do transaction_history1
        self.assertEqual(transaction_history1.total_shares, 100) # OK
        transaction_history2 = TransactionsHistory.objects.filter(transaction=wege_transaction2).first()
        # verificamos a quantidade de shares_amount do transaction_history2
        self.assertEqual(transaction_history2.total_shares, 150) # OK este é que deve valer para este caso

        # delete wege_transaction2
        wege_transaction2.delete()
        
        # Verificamos se o transaction_history2 foi apagado
        transaction_history2 = TransactionsHistory.objects.filter(transaction=wege_transaction2).first()
        self.assertIsNone(transaction_history2)

        # Verificamos se o transaction_history1 está presente e tem total_shares correto
        transaction_history1.refresh_from_db()
        self.assertEqual(transaction_history1.total_shares, 100)

        # Verificamos se existe um PortfolioInvestment criado para essas AssetTransactions
        portfolio_investment = PortfolioInvestment.objects.filter(
            asset=self.asset_wege3,
            portfolio=self.portfolio,
            broker=self.broker_inter,
            ).first()

        self.assertIsNotNone(portfolio_investment) 

        # Verifica se foi criado apenas um PortfolioDividend ou dois
        portfolio_dividends = PortfolioDividend.objects.filter(portfolio_investment=portfolio_investment)
        self.assertEqual(portfolio_dividends.count(), 1)

        # get this PortfolioDividend
        portfolio_dividend = portfolio_dividends.first()

        # Verificamos se o shares_amount do PortfolioDividend é correto
        self.assertEqual(portfolio_dividend.shares_amount, 100)


    def test_multiple_transactions_before_dividend_single_dividend_delete_one(self):
        # Primeiro, criamos um Dividend em um dia qualquer.
        dividend_wege = Dividend.objects.create(
            asset=self.asset_wege3, 
            value_per_share_brl=2, 
            value_per_share_usd=0.4, 
            record_date='2020-01-01',
            pay_date='2020-01-02')

        # verificamos se o dividendo foi criado corretamente
        self.assertIsNotNone(dividend_wege)

        # Criamos duas AssetTransactions com o transaction date antes do record_date do Dividend
        wege_transaction1 = AssetTransaction.objects.create(
            asset=self.asset_wege3,
            portfolio=self.portfolio,
            broker=self.broker_inter,
            transaction_type='buy',
            transaction_date='2019-12-22',
            transaction_amount=100,
            price_brl=10,
            price_usd=2,
            )

        wege_transaction2 = AssetTransaction.objects.create(
            asset=self.asset_wege3,
            portfolio=self.portfolio,
            broker=self.broker_inter,
            transaction_type='buy',
            transaction_date='2019-12-23',
            transaction_amount=50,
            price_brl=10,
            price_usd=2,
            )

        # Verificamos se as AssetTransactions foram criadas corretamente
        self.assertIsNotNone(wege_transaction1) 
        self.assertIsNotNone(wege_transaction2) 

        # Recuperamos as instâncias TransactionsHistory associadas a essas AssetTransactions
        transaction_history1 = TransactionsHistory.objects.filter(transaction=wege_transaction1).first()
        # verificamos a quantidade de shares_amount do transaction_history1
        self.assertEqual(transaction_history1.total_shares, 100) # OK
        transaction_history2 = TransactionsHistory.objects.filter(transaction=wege_transaction2).first()
        # verificamos a quantidade de shares_amount do transaction_history2
        self.assertEqual(transaction_history2.total_shares, 150) # OK este é que deve valer para este caso

        # delete wege_transaction2
        wege_transaction2.delete()
        
        # Verificamos se o transaction_history2 foi apagado
        transaction_history2 = TransactionsHistory.objects.filter(transaction=wege_transaction2).first()
        self.assertIsNone(transaction_history2)

        # Verificamos se o transaction_history1 está presente e tem total_shares correto
        transaction_history1.refresh_from_db()
        self.assertEqual(transaction_history1.total_shares, 100)

        # Verificamos se existe um PortfolioInvestment criado para essas AssetTransactions
        portfolio_investment = PortfolioInvestment.objects.filter(
            asset=self.asset_wege3,
            portfolio=self.portfolio,
            broker=self.broker_inter,
            ).first()

        self.assertIsNotNone(portfolio_investment) 

        # Verifica se foi criado apenas um PortfolioDividend ou dois
        portfolio_dividends = PortfolioDividend.objects.filter(portfolio_investment=portfolio_investment)
        self.assertEqual(portfolio_dividends.count(), 1)

        # get this PortfolioDividend
        portfolio_dividend = portfolio_dividends.first()

        # Verificamos se o shares_amount do PortfolioDividend é correto
        self.assertEqual(portfolio_dividend.shares_amount, 100)


class TransactionHistoryTest(CommonSetupMixin, TestCase):
    def test_multiple_transactions_before_dividend_single_dividend_edit_one(self):
            # Primeiro, criamos um Dividend em um dia qualquer.
        dividend_wege = Dividend.objects.create(
            asset=self.asset_wege3, 
            value_per_share_brl=2, 
            value_per_share_usd=0.4, 
            record_date='2020-01-01',
            pay_date='2020-01-02')

        # verificamos se o dividendo foi criado corretamente
        self.assertIsNotNone(dividend_wege)

        # Criamos duas AssetTransactions com o transaction date antes do record_date do Dividend
        wege_transaction1 = AssetTransaction.objects.create(
            asset=self.asset_wege3,
            portfolio=self.portfolio,
            broker=self.broker_inter,
            transaction_type='buy',
            transaction_date='2019-12-22',
            transaction_amount=100,
            price_brl=10,
            price_usd=2,
            )

        wege_transaction2 = AssetTransaction.objects.create(
            asset=self.asset_wege3,
            portfolio=self.portfolio,
            broker=self.broker_inter,
            transaction_type='buy',
            transaction_date='2019-12-23',
            transaction_amount=50,
            price_brl=10,
            price_usd=2,
            )

        # Verificamos se as AssetTransactions foram criadas corretamente
        self.assertIsNotNone(wege_transaction1) 
        self.assertIsNotNone(wege_transaction2) 

        # Recuperamos as instâncias TransactionsHistory associadas a essas AssetTransactions
        transaction_history1 = TransactionsHistory.objects.filter(transaction=wege_transaction1).first()
        # verificamos a quantidade de shares_amount do transaction_history1
        self.assertEqual(transaction_history1.total_shares, 100) # OK
        transaction_history2 = TransactionsHistory.objects.filter(transaction=wege_transaction2).first()
        # verificamos a quantidade de shares_amount do transaction_history2
        self.assertEqual(transaction_history2.total_shares, 150) # OK este é que deve valer para este caso


        # editamos a primeira transaction para que ela fique com 50 shares_amount
        wege_transaction1.transaction_amount = 50
        wege_transaction1.save()

        # Verificamos se as AssetTransactions foram editadas corretamente
        wege_transaction1.refresh_from_db()
        self.assertEqual(wege_transaction1.transaction_amount, 50) # OK

        # Verificamos se as TransactionsHistory foram editadas corretamente
        transaction_history1.refresh_from_db()
        self.assertEqual(transaction_history1.total_shares, 50)

        transaction_history2.refresh_from_db()
        self.assertEqual(transaction_history2.total_shares, 100)
