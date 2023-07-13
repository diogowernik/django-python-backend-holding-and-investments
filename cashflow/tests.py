from django.test import TestCase
from portfolios.models import PortfolioInvestment
from cashflow.models import CurrencyTransaction, CurrencyTransfer, InternationalCurrencyTransfer
from django.utils import timezone
from common.tests import CommonSetupMixin # criado por mim para facilitar a criação de objetos para testes
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

class CurrencyTransactionSetPricesTests(CommonSetupMixin, TestCase):
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
    def create_transaction(self, portfolio, broker, transaction_type, amount):
        return CurrencyTransaction.objects.create(
            portfolio=portfolio,
            broker=broker,
            transaction_type=transaction_type,
            transaction_amount=amount
        )
    
    def create_transfer(self, portfolio, from_broker, to_broker, amount):
        return CurrencyTransfer.objects.create(
            portfolio=portfolio,
            from_broker=from_broker,
            to_broker=to_broker,
            transfer_amount=amount,
            transfer_date=timezone.now()
        )

    def test_transfer_brl(self):
        transfer_amount = 500
        self.create_transaction(self.portfolio, self.broker_banco_brasil, 'deposit', transfer_amount)
        transfer = self.create_transfer(self.portfolio, self.broker_banco_brasil, self.broker_itau, transfer_amount)
        
        # Vamos verificar se a transação de saque foi criada corretamente
        self.assertEqual(transfer.from_transaction.transaction_amount, transfer_amount)
        self.assertEqual(transfer.from_transaction.broker, self.broker_banco_brasil)
        self.assertEqual(transfer.from_transaction.transaction_type, 'withdraw')

        # Vamos verificar se a transação de deposito foi criada corretamente
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
        transfer_amount = 500
        self.create_transaction(self.portfolio, self.broker_banco_brasil, 'deposit', transfer_amount * 2)
        transfer1 = self.create_transfer(self.portfolio, self.broker_banco_brasil, self.broker_itau, transfer_amount)
        transfer2 = self.create_transfer(self.portfolio, self.broker_banco_brasil, self.broker_itau, transfer_amount)

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

        # Usamos a função create_transaction para depositar o dinheiro
        deposit = self.create_transaction(self.portfolio, self.broker_banco_brasil, 'deposit', transfer_amount * 3)

        # Usamos a função create_transfer para criar as transferências
        transfer1 = self.create_transfer(self.portfolio, self.broker_banco_brasil, self.broker_itau, transfer_amount)
        transfer2 = self.create_transfer(self.portfolio, self.broker_banco_brasil, self.broker_itau, transfer_amount)
        transfer3 = self.create_transfer(self.portfolio, self.broker_banco_brasil, self.broker_itau, transfer_amount)

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

class InternationalCurrencyTransferTest(CommonSetupMixin, TestCase):
    
    def create_international_transfer(self, portfolio, from_broker, to_broker, transfer_amount, exchange_rate):
        return InternationalCurrencyTransfer.objects.create(
            portfolio=portfolio,
            from_broker=from_broker,
            to_broker=to_broker,
            from_transfer_amount=transfer_amount,
            exchange_rate=exchange_rate
        )

    def verify_transfer(self, transfer, from_broker, to_broker, transfer_amount, exchange_rate):
        self.assertEqual(transfer.from_broker, from_broker)
        self.assertEqual(transfer.to_broker, to_broker)
        self.assertEqual(transfer.from_transfer_amount, transfer_amount)
        self.assertEqual(transfer.to_transfer_amount, transfer_amount / exchange_rate)  
        self.assertEqual(transfer.exchange_rate, exchange_rate)
        self.assertIsNotNone(transfer.transfer_date)

        from_transaction = CurrencyTransaction.objects.get(id=transfer.from_transaction.id)
        to_transaction = CurrencyTransaction.objects.get(id=transfer.to_transaction.id)
        self.assertEqual(from_transaction.transaction_amount, transfer_amount)
        self.assertEqual(to_transaction.transaction_amount, transfer_amount / exchange_rate)

        self.assertEqual(from_transaction.transaction_type, 'withdraw')
        self.assertEqual(to_transaction.transaction_type, 'deposit')

    def test_from_brl_broker_to_usd_broker(self):
        transfer_amount_brl = 5000.0
        exchange_rate = 5.0

        transfer = self.create_international_transfer(self.portfolio, self.broker_banco_brasil, self.broker_avenue, transfer_amount_brl, exchange_rate)
        self.verify_transfer(transfer, self.broker_banco_brasil, self.broker_avenue, transfer_amount_brl, exchange_rate)
      
    def test_from_usd_broker_to_brl_broker(self):
        transfer_amount_usd = 1000.0
        exchange_rate = 0.20

        transfer = self.create_international_transfer(self.portfolio, self.broker_avenue, self.broker_banco_brasil, transfer_amount_usd, exchange_rate)
        self.verify_transfer(transfer, self.broker_avenue, self.broker_banco_brasil, transfer_amount_usd, exchange_rate)

    def edit_and_verify_transfer(self, transfer, new_transfer_amount, new_exchange_rate):
        transfer.from_transfer_amount = new_transfer_amount
        transfer.exchange_rate = new_exchange_rate
        transfer.save()

        transfer.refresh_from_db()

        self.assertEqual(transfer.from_transfer_amount, new_transfer_amount)
        self.assertEqual(transfer.to_transfer_amount, new_transfer_amount / new_exchange_rate)
        self.assertEqual(transfer.exchange_rate, new_exchange_rate)

        from_transaction = CurrencyTransaction.objects.get(id=transfer.from_transaction.id)
        to_transaction = CurrencyTransaction.objects.get(id=transfer.to_transaction.id)
        self.assertEqual(from_transaction.transaction_amount, new_transfer_amount)
        self.assertEqual(to_transaction.transaction_amount, new_transfer_amount / new_exchange_rate)

    def delete_and_verify_transfer(self, transfer):
        from_transaction_id = transfer.from_transaction.id
        to_transaction_id = transfer.to_transaction.id

        transfer.delete()

        with self.assertRaises(InternationalCurrencyTransfer.DoesNotExist):
            InternationalCurrencyTransfer.objects.get(id=transfer.id)

        with self.assertRaises(CurrencyTransaction.DoesNotExist):
            CurrencyTransaction.objects.get(id=from_transaction_id)
        with self.assertRaises(CurrencyTransaction.DoesNotExist):
            CurrencyTransaction.objects.get(id=to_transaction_id)

    def test_edit_international_currency_transfer(self):
        transfer_amount_usd = 1000.0
        exchange_rate = 0.20
        new_transfer_amount_usd = 500.0
        new_exchange_rate = 0.25

        transfer = self.create_international_transfer(self.portfolio, self.broker_avenue, self.broker_banco_brasil, transfer_amount_usd, exchange_rate)
        self.edit_and_verify_transfer(transfer, new_transfer_amount_usd, new_exchange_rate)

    def test_delete_international_currency_transfer(self):
        transfer_amount_usd = 1000.0
        exchange_rate = 0.20

        transfer = self.create_international_transfer(self.portfolio, self.broker_avenue, self.broker_banco_brasil, transfer_amount_usd, exchange_rate)
        self.delete_and_verify_transfer(transfer)
