from django.test import TestCase
from portfolios.models import PortfolioInvestment,Portfolio
from investments.models import CurrencyHolding, Stocks, BrStocks, Reit
from brokers.models import Broker, Currency, CurrencyHistoricalPrice
from cashflow.models import CurrencyTransaction, AssetTransaction, CurrencyTransfer, InternationalCurrencyTransfer
from categories.models import Category, SubCategory
from django.contrib.auth.models import User
from django.utils import timezone
from common.tests import CommonSetupMixin # criado por mim para facilitar a criação de objetos para testes
from unittest.mock import patch
from datetime import datetime, timedelta

class CurrencyTransactionTest(CommonSetupMixin, TestCase):      
    def create_transaction(self, amount, price_brl, price_usd, transaction_type='deposit', broker=None):
        # Método auxiliar para criar transações.
        return CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=broker or self.broker_banco_brasil, transaction_type=transaction_type, transaction_amount=amount, price_brl=price_brl, price_usd=price_usd)

    def test_brl_banco_brasil_currency_transactions(self):
        # Teste para garantir que as transações em BRL com broker brl funcionam, 
        # cria 4 transações de 1000 reais cada e verifica se o saldo final está correto
        for i in range(4):
            transaction = self.create_transaction(1000, 1, 0.20)
            self.assertEqual(PortfolioInvestment.objects.get(id=transaction.portfolio_investment.id).shares_amount, 1000 * (i + 1))

    def test_usd_currency_transactions(self):
        # Teste para garantir que as transações em USD com broker usd funcionam, 
        # cria 4 transações de 1000 dolares cada e verifica se o saldo final está correto
        for i in range(4):
            transaction = self.create_transaction(1000, 5, 1, broker=self.broker_avenue)
            self.assertEqual(PortfolioInvestment.objects.get(id=transaction.portfolio_investment.id).shares_amount, 1000 * (i + 1))

    def test_eur_currency_transactions(self):
        # Teste para garantir que as transações em EUR com broker eur funcionam, 
        # cria 4 transações de 1000 euros cada e verifica se o saldo final está correto
        for i in range(4):
            transaction = self.create_transaction(1000, 6, 1.2, broker=self.broker_degiro)
            self.assertEqual(PortfolioInvestment.objects.get(id=transaction.portfolio_investment.id).shares_amount, 1000 * (i + 1))

    def test_brl_currency_withdraw(self):
        # Teste para garantir que as retiradas em BRL estão funcionando corretamente.
        # Realiza um depósito inicial de 2000 e em seguida faz duas retiradas de 500. 
        # Verifica se o saldo final está correto após cada retirada.
        self.create_transaction(2000, 1, 0.20)
        transaction1 = self.create_transaction(500, 1, 0.20, transaction_type='withdraw')
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction1.portfolio_investment.id).shares_amount, 1500)
        transaction2 = self.create_transaction(500, 1, 0.20, transaction_type='withdraw')
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction2.portfolio_investment.id).shares_amount, 1000)

    def test_edit_first_brl_currency_transaction(self):
        # Teste para verificar se a edição de transações em BRL está funcionando corretamente.
        # Cria 4 transações de 1000 cada, edita a primeira transação aumentando seu valor para 2000,
        # e verifica se o saldo final reflete essa alteração.
        transactions = [self.create_transaction(1000, 1, 0.20) for _ in range(4)]
        transactions[0].transaction_amount = 2000
        transactions[0].save()
        self.assertEqual(PortfolioInvestment.objects.get(id=transactions[0].portfolio_investment.id).shares_amount, 5000)

    def test_edit_first_brl_currency_transaction_with_two_brokers(self):
        # Teste para verificar se a edição da primeira transação funciona corretamente quando há dois brokers envolvidos.
        # Criamos três transações com o broker banco do brasil e uma com o corretor Itau.
        # Em seguida, editamos a primeira transação, mudando o valor da transação, e verificamos se as quantidades de ações no PortfolioInvestment estão corretas.
        transactions = [self.create_transaction(1000, 1, 0.20) for _ in range(2)]
        transactions.append(self.create_transaction(1000, 1, 0.20, broker=self.broker_itau))
        transactions.append(self.create_transaction(1000, 1, 0.20))
        transactions[0].transaction_amount = 2000
        transactions[0].save()
        self.assertEqual(PortfolioInvestment.objects.get(id=transactions[0].portfolio_investment.id).shares_amount, 4000)
        self.assertEqual(PortfolioInvestment.objects.get(id=transactions[2].portfolio_investment.id).shares_amount, 1000)

    def test_delete_brl_currency_transaction(self):
        # Teste para verificar se a deleção de transações está funcionando corretamente.
        # Criamos duas transações e em seguida deletamos a primeira. Verificamos se a quantidade de ações restante no PortfolioInvestment é a esperada.
        transactions = [self.create_transaction(1000, 1, 0.20) for _ in range(2)]
        transactions[0].delete()
        self.assertEqual(PortfolioInvestment.objects.get(id=transactions[1].portfolio_investment.id).shares_amount, 1000)

    # set_prices tests yesterday (get historical price)
    def create_transaction_no_price(self, amount, transaction_type='deposit', broker=None, transaction_date=None):
        # Método auxiliar para criar transações sem preço definido.
        return CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=broker or self.broker_banco_brasil, transaction_type=transaction_type, transaction_amount=amount, transaction_date=transaction_date or timezone.now())

    def test_set_prices_brl_banco_brasil(self):
        # Teste para verificar se o método set_prices está funcionando corretamente para BRL
        yesterday = datetime.now() - timedelta(days=1)
        transaction = self.create_transaction_no_price(1000, broker=self.broker_banco_brasil, transaction_date=yesterday)
        transaction.save()
        self.assertEqual(transaction.price_brl, 1)
        self.assertEqual(transaction.price_usd, 0.18)  # Obtido a partir dos dados históricos

    def test_set_prices_usd_avenue(self):
        # Teste para verificar se o método set_prices está funcionando corretamente para USD
        yesterday = datetime.now() - timedelta(days=1)
        transaction = self.create_transaction_no_price(1000, broker=self.broker_avenue, transaction_date=yesterday)
        transaction.save()
        self.assertEqual(transaction.price_brl, 5.5)  # Obtido a partir dos dados históricos
        self.assertEqual(transaction.price_usd, 1)

    def test_set_prices_eur_degiro(self):
        # Teste para verificar se o método set_prices está funcionando corretamente para EUR
        yesterday = datetime.now() - timedelta(days=1)
        transaction = self.create_transaction_no_price(1000, broker=self.broker_degiro, transaction_date=yesterday)
        transaction.save()
        self.assertEqual(transaction.price_brl, 6.5)  # Obtido a partir dos dados históricos
        self.assertEqual(transaction.price_usd, 1.15)  # Obtido a partir dos dados históricos
    # set_prices tests today (get current price)

    def test_set_prices_brl_banco_brasil_today(self):
        # Teste para verificar se o método set_prices está funcionando corretamente para BRL
        transaction = self.create_transaction_no_price(1000, broker=self.broker_banco_brasil, transaction_date=datetime.today())
        transaction.save()
        self.assertEqual(transaction.price_brl, 1)
        self.assertEqual(transaction.price_usd, 0.20)  # Obtido a partir da definição da moeda no setUp

    def test_set_prices_usd_avenue_today(self):
        # Teste para verificar se o método set_prices está funcionando corretamente para USD
        transaction = self.create_transaction_no_price(1000, broker=self.broker_avenue, transaction_date=datetime.today())
        transaction.save()
        self.assertEqual(transaction.price_brl, 5)  # Obtido a partir da definição da moeda no setUp
        self.assertEqual(transaction.price_usd, 1)

class CurrencyTransactionCalculationTest(CommonSetupMixin, TestCase):
    def create_transaction(self, amount, price_brl, price_usd, transaction_type='deposit', broker=None):
        # Método auxiliar para criar transações.
        return CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=broker or self.broker_banco_brasil, transaction_type=transaction_type, transaction_amount=amount, price_brl=price_brl, price_usd=price_usd)

    def test_average_price_calculation_three_transactions(self):
        # Teste para verificar se o cálculo do preço médio está funcionando corretamente.
        # Criamos três transações com diferentes preços e calculamos o preço médio esperado.
        # Em seguida, verificamos se o preço médio armazenado no PortfolioInvestment corresponde ao preço médio esperado.
        prices_brl = [5.12, 8.14, 12.76]
        prices_usd = [10.25, 16.28, 25.52]
        transactions = [self.create_transaction(1000, brl, usd) for brl, usd in zip(prices_brl, prices_usd)]

        total_cost_brl = sum(t.transaction_amount * t.price_brl for t in transactions)
        total_cost_usd = sum(t.transaction_amount * t.price_usd for t in transactions)
        total_shares = sum(t.transaction_amount for t in transactions)

        expected_average_price_brl = total_cost_brl / total_shares
        expected_average_price_usd = total_cost_usd / total_shares

        portfolio_investment = PortfolioInvestment.objects.get(id=transactions[-1].portfolio_investment.id)
        self.assertEqual(portfolio_investment.share_average_price_brl, expected_average_price_brl)
        self.assertEqual(portfolio_investment.share_average_price_usd, expected_average_price_usd)

    def calculate_expected_average_price(self, transactions):
        # Este é um método auxiliar para calcular o preço médio esperado dada uma lista de transações.
        # Primeiro, calculamos o custo total em BRL e USD e o total de ações.
        # Em seguida, calculamos o preço médio esperado em BRL e USD, dividindo o custo total pelo total de ações.
        # Finalmente, retornamos ambos os preços médios esperados.
        total_cost_brl = sum(t.transaction_amount * t.price_brl for t in transactions)
        total_cost_usd = sum(t.transaction_amount * t.price_usd for t in transactions)
        total_shares = sum(t.transaction_amount for t in transactions)

        expected_average_price_brl = total_cost_brl / total_shares
        expected_average_price_usd = total_cost_usd / total_shares

        return expected_average_price_brl, expected_average_price_usd

    def test_average_price_calculation_with_deletion(self):
        # Teste para verificar se o cálculo do preço médio está funcionando corretamente após a deletar de uma transação.
        # Primeiro, criamos quatro transações e em seguida deletamos a segunda transação.
        # Em seguida, calculamos o preço médio esperado usando as três transações restantes.
        # Finalmente, verificamos se o preço médio armazenado no PortfolioInvestment corresponde ao preço médio esperado.
        transaction1 = self.create_transaction(1000, 5.12, 10.25)
        transaction2 = self.create_transaction(1000, 8.14, 16.28)
        transaction3 = self.create_transaction(1000, 12.76, 25.52)
        transaction4 = self.create_transaction(1000, 18.34, 36.68)

        # Deletamos a transação 2
        transaction2.delete()

        # Obtemos os valores de preço médio esperados
        expected_average_price_brl, expected_average_price_usd = self.calculate_expected_average_price([transaction1, transaction3, transaction4])

        # Verificamos se os preços médios armazenados no PortfolioInvestment correspondem aos preços médios esperados
        portfolio_investment = PortfolioInvestment.objects.get(portfolio=self.portfolio, broker=self.broker_banco_brasil)
        self.assertAlmostEqual(portfolio_investment.share_average_price_brl, expected_average_price_brl)
        self.assertAlmostEqual(portfolio_investment.share_average_price_usd, expected_average_price_usd)

    def test_average_price_calculation_with_edit(self):
        # Teste para verificar se o cálculo do preço médio está funcionando corretamente após a edição de uma transação.
        # Primeiro, criamos quatro transações e em seguida editamos a terceira transação, modificando a quantidade e os preços.
        # Em seguida, calculamos o preço médio esperado usando as quatro transações, incluindo a transação editada.
        # Finalmente, verificamos se o preço médio armazenado no PortfolioInvestment corresponde ao preço médio esperado.
        transaction1 = self.create_transaction(1000, 5.12, 10.25)
        transaction2 = self.create_transaction(1000, 8.14, 16.28)
        transaction3 = self.create_transaction(1000, 12.76, 25.52)
        transaction4 = self.create_transaction(1000, 18.34, 36.68)

        # Modificamos a transaction3
        transaction3.transaction_amount = 1500
        transaction3.price_brl = 21.85
        transaction3.price_usd = 43.70
        transaction3.save()

        # Obtemos os valores de preço médio esperados
        expected_average_price_brl, expected_average_price_usd = self.calculate_expected_average_price([transaction1, transaction2, transaction3, transaction4])

        # Verificamos se os preços médios armazenados no PortfolioInvestment correspondem aos preços médios esperados
        portfolio_investment = PortfolioInvestment.objects.get(portfolio=self.portfolio, broker=self.broker_banco_brasil)
        self.assertAlmostEqual(portfolio_investment.share_average_price_brl, expected_average_price_brl)
        self.assertAlmostEqual(portfolio_investment.share_average_price_usd, expected_average_price_usd)

class CurrencyTransferTest(CommonSetupMixin, TestCase):
    # criar um def create_transacttion e um def create_transfer para otimizar o código

    # reduzir o código aqui
    def test_transfer_brl(self):
        # Vamos fazer uma transferência de 500 BRL do banco do brasil para o Itau
        transfer_amount = 500

        # Primeiro, vamos depositar o dinheiro no banco do brasil
        deposit = CurrencyTransaction.objects.create(
            portfolio=self.portfolio,
            broker=self.broker_banco_brasil,
            transaction_type='deposit',
            transaction_amount=transfer_amount
        )

        # Agora vamos criar a transferência
        transfer = CurrencyTransfer.objects.create(
            portfolio=self.portfolio,
            from_broker=self.broker_banco_brasil,
            to_broker=self.broker_itau,
            transfer_amount=transfer_amount,
            transfer_date=timezone.now()
        )

        # Vamos verificar se a transação de saída foi criada corretamente
        self.assertEqual(transfer.from_transaction.transaction_amount, transfer_amount)
        self.assertEqual(transfer.from_transaction.broker, self.broker_banco_brasil)
        self.assertEqual(transfer.from_transaction.transaction_type, 'withdraw')

        # Vamos verificar se a transação de entrada foi criada corretamente
        self.assertEqual(transfer.to_transaction.transaction_amount, transfer_amount)
        self.assertEqual(transfer.to_transaction.broker, self.broker_itau)
        self.assertEqual(transfer.to_transaction.transaction_type, 'deposit')

        # Vamos verificar se o saldo do broker de origem foi atualizado corretamente
        banco_brasil_investment = PortfolioInvestment.objects.get(portfolio=self.portfolio, broker=self.broker_banco_brasil, asset=self.asset_brl)
        self.assertEqual(banco_brasil_investment.shares_amount, 0)

        # Vamos verificar se o saldo do broker de destino foi atualizado corretamente
        itau_investment = PortfolioInvestment.objects.get(portfolio=self.portfolio, broker=self.broker_itau, asset=self.asset_brl)
        self.assertEqual(itau_investment.shares_amount, transfer_amount)

    def test_delete_transfer_brl(self):
        # Vamos fazer duas transferências de 500 BRL cada do banco do brasil para o Itau
        transfer_amount = 500

        # Primeiro, vamos depositar o dinheiro no banco do brasil
        deposit = CurrencyTransaction.objects.create(
            portfolio=self.portfolio,
            broker=self.broker_banco_brasil,
            transaction_type='deposit',
            transaction_amount=transfer_amount * 2
        )

        # Agora vamos criar a primeira transferência
        transfer1 = CurrencyTransfer.objects.create(
            portfolio=self.portfolio,
            from_broker=self.broker_banco_brasil,
            to_broker=self.broker_itau,
            transfer_amount=transfer_amount,
            transfer_date=timezone.now()
        )

        # E a segunda transferência
        transfer2 = CurrencyTransfer.objects.create(
            portfolio=self.portfolio,
            from_broker=self.broker_banco_brasil,
            to_broker=self.broker_itau,
            transfer_amount=transfer_amount,
            transfer_date=timezone.now()
        )

        # Agora vamos deletar a primeira transferência
        transfer1.delete()

        # Vamos verificar se a transação de saída da primeira transferência foi deletada corretamente
        with self.assertRaises(CurrencyTransaction.DoesNotExist):
            transfer1.from_transaction.refresh_from_db()

        # E a transação de entrada da primeira transferência
        with self.assertRaises(CurrencyTransaction.DoesNotExist):
            transfer1.to_transaction.refresh_from_db()

        # Vamos verificar se o saldo do broker de origem foi atualizado corretamente
        banco_brasil_investment = PortfolioInvestment.objects.get(portfolio=self.portfolio, broker=self.broker_banco_brasil, asset=self.asset_brl)
        self.assertEqual(banco_brasil_investment.shares_amount, transfer_amount)

        # Vamos verificar se o saldo do broker de destino foi atualizado corretamente
        itau_investment = PortfolioInvestment.objects.get(portfolio=self.portfolio, broker=self.broker_itau, asset=self.asset_brl)
        self.assertEqual(itau_investment.shares_amount, transfer_amount)

        # Vamos verificar se as transações da segunda transferência ainda existem
        transfer2.from_transaction.refresh_from_db()
        transfer2.to_transaction.refresh_from_db()

    def test_edit_transfer_brl(self):
        # Vamos fazer três transferências de 500 BRL cada do banco do brasil para o Itau
        transfer_amount = 500

        # Primeiro, vamos depositar o dinheiro no banco do brasil
        deposit = CurrencyTransaction.objects.create(
            portfolio=self.portfolio,
            broker=self.broker_banco_brasil,
            transaction_type='deposit',
            transaction_amount=transfer_amount * 3
        )

        # Agora vamos criar as transferências
        transfer1 = CurrencyTransfer.objects.create(
            portfolio=self.portfolio,
            from_broker=self.broker_banco_brasil,
            to_broker=self.broker_itau,
            transfer_amount=transfer_amount,
            transfer_date=timezone.now()
        )

        transfer2 = CurrencyTransfer.objects.create(
            portfolio=self.portfolio,
            from_broker=self.broker_banco_brasil,
            to_broker=self.broker_itau,
            transfer_amount=transfer_amount,
            transfer_date=timezone.now()
        )

        transfer3 = CurrencyTransfer.objects.create(
            portfolio=self.portfolio,
            from_broker=self.broker_banco_brasil,
            to_broker=self.broker_itau,
            transfer_amount=transfer_amount,
            transfer_date=timezone.now()
        )

        # Agora vamos editar a quantidade transferida na segunda transferência
        edited_amount = 700
        transfer2.transfer_amount = edited_amount
        transfer2.save()

        # Vamos verificar se a transação de saída da segunda transferência foi editada corretamente
        transfer2.from_transaction.refresh_from_db()
        self.assertEqual(transfer2.from_transaction.transaction_amount, edited_amount)

        # E a transação de entrada da segunda transferência
        transfer2.to_transaction.refresh_from_db()
        self.assertEqual(transfer2.to_transaction.transaction_amount, edited_amount)

        # Vamos verificar se o saldo do broker de origem foi atualizado corretamente
        # Depois de três transferências de 500 e uma edição para 700, o saldo deve ser -700 (1500 depositados - 500 - 700 - 500)
        banco_brasil_investment = PortfolioInvestment.objects.get(portfolio=self.portfolio, broker=self.broker_banco_brasil, asset=self.asset_brl)
        self.assertEqual(banco_brasil_investment.shares_amount, deposit.transaction_amount - transfer_amount - transfer_amount - edited_amount)

        # Vamos verificar se o saldo do broker de destino foi atualizado corretamente
        # Depois de receber três transferências de 500 e uma edição para 700, o saldo deve ser 1700 (500 + 700 + 500)
        itau_investment = PortfolioInvestment.objects.get(portfolio=self.portfolio, broker=self.broker_itau, asset=self.asset_brl)
        self.assertEqual(itau_investment.shares_amount, transfer_amount + edited_amount + transfer_amount)

class AssetTransactionTest(CommonSetupMixin, TestCase):
    def test_brl_banco_do_brasil_asset_buy(self):
        transaction1 = AssetTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=100, price_brl=10, price_usd=2)
        transaction2 = AssetTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=200, price_brl=20, price_usd=4)
        transaction3 = AssetTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=300, price_brl=30, price_usd=6)

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
        transaction1 = AssetTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=100, price_brl=10, price_usd=2)
        transaction2 = AssetTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=200, price_brl=20, price_usd=4)
        transaction3 = AssetTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=300, price_brl=30, price_usd=6)
        transaction4 = AssetTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='sell', asset=self.asset_wege3, transaction_amount=400, price_brl=40, price_usd=8)

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
        transaction1 = AssetTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=100, price_brl=10, price_usd=2)
        transaction2 = AssetTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=200, price_brl=20, price_usd=4)
        transaction3 = AssetTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=300, price_brl=30, price_usd=6)

        # Deleta a segunda transação
        transaction2_id = transaction2.id
        transaction2.delete()

        # Verifica se a transação foi deletada corretamente
        with self.assertRaises(AssetTransaction.DoesNotExist):
            AssetTransaction.objects.get(id=transaction2_id)

        # Verifica se o portfolio investment foi atualizado corretamente
        portfolio_investment = PortfolioInvestment.objects.get(id=transaction3.portfolio_investment.id)
        self.assertEqual(portfolio_investment.shares_amount, 400)  # 100 + 300
        self.assertEqual(portfolio_investment.total_cost_brl, 10000)  # 1000 + 9000
        self.assertEqual(portfolio_investment.share_average_price_brl, 25)  # 10000 / 400

        # Verifica se a CurrencyTransaction correspondente à transação deletada também foi deletada
        currency_transactions = CurrencyTransaction.objects.filter(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_date=transaction2.transaction_date)
        self.assertEqual(len(currency_transactions), 0)

    def test_brl_broker_diff_asset_no_delete(self):
        transaction1 = AssetTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=100, price_brl=10, price_usd=2)
        transaction2 = AssetTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_itau, transaction_type='buy', asset=self.asset_wege3, transaction_amount=200, price_brl=20, price_usd=4)
        transaction3 = AssetTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=300, price_brl=30, price_usd=6)

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
        transaction1 = AssetTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=100, price_brl=10, price_usd=2)
        transaction2 = AssetTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=200, price_brl=20, price_usd=4)
        transaction3 = AssetTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='buy', asset=self.asset_wege3, transaction_amount=300, price_brl=30, price_usd=6)

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

class InternationalCurrencyTransferTest(CommonSetupMixin, TestCase):
    def test_from_brl_broker_to_usd_broker(self):
        # Definimos o valor a ser transferido e a taxa de câmbio
        transfer_amount_brl = 5000.0  # 5000 BRL
        exchange_rate = 5.0  # 1 USD = 5 BRL

        # Criamos a transferência
        transfer = InternationalCurrencyTransfer.objects.create(
            portfolio=self.portfolio,
            from_broker=self.broker_banco_brasil,
            to_broker=self.broker_avenue,
            from_transfer_amount=transfer_amount_brl,
            exchange_rate=exchange_rate
        )

        # Testamos se a transferência foi criada corretamente
        self.assertEqual(transfer.from_broker, self.broker_banco_brasil)
        self.assertEqual(transfer.to_broker, self.broker_avenue)
        self.assertEqual(transfer.from_transfer_amount, transfer_amount_brl)
        self.assertEqual(transfer.to_transfer_amount, transfer_amount_brl / exchange_rate)  # O valor em USD
        self.assertEqual(transfer.exchange_rate, exchange_rate)
        self.assertIsNotNone(transfer.transfer_date)

        # Verificamos se as transações foram criadas corretamente
        from_transaction = CurrencyTransaction.objects.get(id=transfer.from_transaction.id)
        to_transaction = CurrencyTransaction.objects.get(id=transfer.to_transaction.id)
        self.assertEqual(from_transaction.transaction_amount, transfer_amount_brl)
        self.assertEqual(to_transaction.transaction_amount, transfer_amount_brl / exchange_rate)

        # Verificamos se o tipo de transação está correto
        self.assertEqual(from_transaction.transaction_type, 'withdraw')
        self.assertEqual(to_transaction.transaction_type, 'deposit')
      
    def test_from_usd_broker_to_brl_broker(self):
        # Definimos o valor a ser transferido e a taxa de câmbio
        transfer_amount_usd = 1000.0  # 1000 USD
        exchange_rate = 0.20  # 1 BRL = 0.20 USD

        # Criamos a transferência
        transfer = InternationalCurrencyTransfer.objects.create(
            portfolio=self.portfolio,
            from_broker=self.broker_avenue,
            to_broker=self.broker_banco_brasil,
            from_transfer_amount=transfer_amount_usd,
            exchange_rate=exchange_rate
        )

        # Testamos se a transferência foi criada corretamente
        self.assertEqual(transfer.from_broker, self.broker_avenue)
        self.assertEqual(transfer.to_broker, self.broker_banco_brasil)
        self.assertEqual(transfer.from_transfer_amount, transfer_amount_usd)
        self.assertEqual(transfer.to_transfer_amount, transfer_amount_usd / exchange_rate)  # O valor em BRL
        self.assertEqual(transfer.exchange_rate, exchange_rate)
        self.assertIsNotNone(transfer.transfer_date)

        # Verificamos se as transações foram criadas corretamente
        from_transaction = CurrencyTransaction.objects.get(id=transfer.from_transaction.id)
        to_transaction = CurrencyTransaction.objects.get(id=transfer.to_transaction.id)
        self.assertEqual(from_transaction.transaction_amount, transfer_amount_usd)
        self.assertEqual(to_transaction.transaction_amount, transfer_amount_usd / exchange_rate)

        # Verificamos se o tipo de transação está correto
        self.assertEqual(from_transaction.transaction_type, 'withdraw')
        self.assertEqual(to_transaction.transaction_type, 'deposit')

    def test_edit_international_currency_transfer(self):
        # Crie um objeto de transferência como em um dos testes anteriores
        transfer_amount_usd = 1000.0
        exchange_rate = 0.20
        transfer = InternationalCurrencyTransfer.objects.create(
            portfolio=self.portfolio,
            from_broker=self.broker_avenue,
            to_broker=self.broker_banco_brasil,
            from_transfer_amount=transfer_amount_usd,
            exchange_rate=exchange_rate
        )

        # Edite o objeto de transferência
        new_transfer_amount_usd = 500.0
        new_exchange_rate = 0.25
        transfer.from_transfer_amount = new_transfer_amount_usd
        transfer.exchange_rate = new_exchange_rate
        transfer.save()

        # Recarregue o objeto de transferência do banco de dados
        transfer.refresh_from_db()

        # Verifique se as edições foram aplicadas corretamente
        self.assertEqual(transfer.from_transfer_amount, new_transfer_amount_usd)
        self.assertEqual(transfer.to_transfer_amount, new_transfer_amount_usd / new_exchange_rate) 
        self.assertEqual(transfer.exchange_rate, new_exchange_rate)

        # Verifique se as transações relacionadas foram atualizadas corretamente
        from_transaction = CurrencyTransaction.objects.get(id=transfer.from_transaction.id)
        to_transaction = CurrencyTransaction.objects.get(id=transfer.to_transaction.id)
        self.assertEqual(from_transaction.transaction_amount, new_transfer_amount_usd)
        self.assertEqual(to_transaction.transaction_amount, new_transfer_amount_usd / new_exchange_rate)
  
    def test_delete_international_currency_transfer(self):
        # Crie um objeto de transferência como em um dos testes anteriores
        transfer_amount_usd = 1000.0
        exchange_rate = 0.20
        transfer = InternationalCurrencyTransfer.objects.create(
            portfolio=self.portfolio,
            from_broker=self.broker_avenue,
            to_broker=self.broker_banco_brasil,
            from_transfer_amount=transfer_amount_usd,
            exchange_rate=exchange_rate
        )

        # Armazene os IDs das transações relacionadas
        from_transaction_id = transfer.from_transaction.id
        to_transaction_id = transfer.to_transaction.id

        # Delete a transferência
        transfer.delete()

        # Verifique se a transferência foi excluída
        with self.assertRaises(InternationalCurrencyTransfer.DoesNotExist):
            InternationalCurrencyTransfer.objects.get(id=transfer.id)

        # Verifique se as transações relacionadas foram excluídas
        with self.assertRaises(CurrencyTransaction.DoesNotExist):
            CurrencyTransaction.objects.get(id=from_transaction_id)
        with self.assertRaises(CurrencyTransaction.DoesNotExist):
            CurrencyTransaction.objects.get(id=to_transaction_id)
