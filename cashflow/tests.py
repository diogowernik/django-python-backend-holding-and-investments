from django.test import TestCase
from portfolios.models import PortfolioInvestment,Portfolio
from investments.models import CurrencyHolding, Stocks, BrStocks, Reit
from brokers.models import Broker, Currency 
from cashflow.models import CurrencyTransaction, AssetTransaction, CurrencyTransfer
from categories.models import Category, SubCategory
from django.contrib.auth.models import User
from django.utils import timezone

class CurrencyTransactionTest(TestCase):
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

    def test_brl_banco_brasil_currency_transactions(self):
        # A partir daqui, você pode usar self.broker, self.currency e self.portfolio para criar suas transações
        transaction1 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=1, price_usd=0.20)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction1.portfolio_investment.id).shares_amount, 1000)

        transaction2 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=1, price_usd=0.20)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction2.portfolio_investment.id).shares_amount, 2000)

        transaction3 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=1, price_usd=0.20)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction3.portfolio_investment.id).shares_amount, 3000)

        transaction4 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=1, price_usd=0.20)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction4.portfolio_investment.id).shares_amount, 4000)

    def test_usd_currency_transactions(self):
        # A partir daqui, você pode usar self.broker_avenue e self.portfolio para criar suas transações
        transaction1 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_avenue, transaction_type='deposit', transaction_amount=1000, price_brl=5, price_usd=1)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction1.portfolio_investment.id).shares_amount, 1000)

        transaction2 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_avenue, transaction_type='deposit', transaction_amount=1000, price_brl=5, price_usd=1)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction2.portfolio_investment.id).shares_amount, 2000)

        transaction3 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_avenue, transaction_type='deposit', transaction_amount=1000, price_brl=5, price_usd=1)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction3.portfolio_investment.id).shares_amount, 3000)

        transaction4 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_avenue, transaction_type='deposit', transaction_amount=1000, price_brl=5, price_usd=1)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction4.portfolio_investment.id).shares_amount, 4000)

    def test_brl_currency_withdraw(self):
        # Primeiro, criamos duas transações de depósito, para que tenhamos algo para retirar.
        CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=2000, price_brl=1, price_usd=0.20)

        # A partir daqui, você pode usar self.broker, self.currency e self.portfolio para criar suas transações
        transaction1 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='withdraw', transaction_amount=500, price_brl=1, price_usd=0.20)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction1.portfolio_investment.id).shares_amount, 1500)

        transaction2 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='withdraw', transaction_amount=500, price_brl=1, price_usd=0.20)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction2.portfolio_investment.id).shares_amount, 1000)

    def test_edit_first_brl_currency_transaction(self):
        # Primeiro, criamos quatro transações de depósito.
        transaction1 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=1, price_usd=0.20)
        transaction2 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=1, price_usd=0.20)
        transaction3 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=1, price_usd=0.20)
        transaction4 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=1, price_usd=0.20)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction4.portfolio_investment.id).shares_amount, 4000)

        # Agora, editamos a primeira transação e verificamos se a quantidade de ações foi atualizada corretamente.
        transaction1.transaction_amount = 2000
        transaction1.save()
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction1.portfolio_investment.id).shares_amount, 5000)

    def test_edit_first_brl_currency_transaction_with_two_brokers(self):
        # Primeiro, criamos quatro transações de depósito.
        transaction1 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=1, price_usd=0.20)
        transaction2 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=1, price_usd=0.20)
        
        # Terceira transação é feita com uma broker diferente.
        transaction3 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_itau, transaction_type='deposit', transaction_amount=1000, price_brl=1, price_usd=0.20)

        transaction4 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=1, price_usd=0.20)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction4.portfolio_investment.id).shares_amount, 3000)

        # Agora, editamos a primeira transação e verificamos se a quantidade de ações foi atualizada corretamente.
        transaction1.transaction_amount = 2000
        transaction1.save()
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction1.portfolio_investment.id).shares_amount, 4000)

        # Também verificamos se a quantidade de ações na broker_itau está correta.
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction3.portfolio_investment.id).shares_amount, 1000)

    def test_delete_brl_currency_transaction(self):
        # Primeiro, criamos duas transações de depósito.
        transaction1 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=1, price_usd=0.20)
        transaction2 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=1, price_usd=0.20)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction2.portfolio_investment.id).shares_amount, 2000)

        # Agora, deletamos a primeira transação e verificamos se a quantidade de ações foi atualizada corretamente.
        transaction1.delete()
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction2.portfolio_investment.id).shares_amount, 1000)

    def test_average_price_calculation_three_transactions(self):
        # Primeiro, atualizamos o preço da Currency para cada transação
        price_brl = 5.12
        price_usd = 10.25
        transaction1 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=price_brl, price_usd=price_usd)

        price_brl = 8.14
        price_usd = 16.28
        transaction2 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=price_brl, price_usd=price_usd)
            
        price_brl = 12.76
        price_usd = 25.52
        transaction3 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=price_brl, price_usd=price_usd)

        # Calculamos o preço médio esperado. O preço médio é a soma do custo de todas as transações dividido pelo número total de ações.
        total_cost_brl = (transaction1.transaction_amount * transaction1.price_brl +
                        transaction2.transaction_amount * transaction2.price_brl +
                        transaction3.transaction_amount * transaction3.price_brl)

        total_cost_usd = (transaction1.transaction_amount * transaction1.price_usd +
                        transaction2.transaction_amount * transaction2.price_usd +
                        transaction3.transaction_amount * transaction3.price_usd)

        total_shares = (transaction1.transaction_amount +
                        transaction2.transaction_amount +
                        transaction3.transaction_amount)

        expected_average_price_brl = total_cost_brl / total_shares
        expected_average_price_usd = total_cost_usd / total_shares


        # Verificamos se o preço médio armazenado no PortfolioInvestment corresponde ao preço médio esperado.
        portfolio_investment = PortfolioInvestment.objects.get(id=transaction3.portfolio_investment.id)
        self.assertEqual(portfolio_investment.share_average_price_brl, expected_average_price_brl)
        self.assertEqual(portfolio_investment.share_average_price_usd, expected_average_price_usd)

    def test_average_price_calculation_with_deletion(self):
        # Primeiro, atualizamos o preço da Currency para cada transação
        price_brl = 5.12
        price_usd = 10.25
        transaction1 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=price_brl, price_usd=price_usd)

        price_brl = 8.14
        price_usd = 16.28
        transaction2 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=price_brl, price_usd=price_usd)

        price_brl = 12.76
        price_usd = 25.52
        transaction3 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=price_brl, price_usd=price_usd)

        price_brl = 18.34
        price_usd = 36.68
        transaction4 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=price_brl, price_usd=price_usd)

        # Agora, deletamos a transação 2
        transaction2.delete()

        # Calculamos o preço médio esperado após a deleção. O preço médio é a soma do custo das transações restantes dividido pelo número total de ações restantes.
        total_cost_brl = (transaction1.transaction_amount * transaction1.price_brl +
                        transaction3.transaction_amount * transaction3.price_brl +
                        transaction4.transaction_amount * transaction4.price_brl)

        total_cost_usd = (transaction1.transaction_amount * transaction1.price_usd +
                        transaction3.transaction_amount * transaction3.price_usd +
                        transaction4.transaction_amount * transaction4.price_usd)

        total_shares = (transaction1.transaction_amount +
                        transaction3.transaction_amount +
                        transaction4.transaction_amount)

        expected_average_price_brl = total_cost_brl / total_shares
        expected_average_price_usd = total_cost_usd / total_shares

        # Verificamos se o preço médio armazenado no PortfolioInvestment corresponde ao preço médio esperado após a deleção da transação 2.
        # Verificamos se o preço médio armazenado no PortfolioInvestment corresponde ao preço médio esperado após a deleção da transação 2.
        portfolio_investment = PortfolioInvestment.objects.get(id=transaction4.portfolio_investment.id)
        self.assertEqual(portfolio_investment.share_average_price_brl, expected_average_price_brl)
        self.assertEqual(portfolio_investment.share_average_price_usd, expected_average_price_usd)

    def test_average_price_calculation_with_edit(self):
        # Primeiro, atualizamos o preço da Currency para cada transação
        self.currency_brl.price_brl = 5.12
        self.currency_brl.price_usd = 10.25
        self.currency_brl.save()
        transaction1 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000)

        self.currency_brl.price_brl = 8.14
        self.currency_brl.price_usd = 16.28
        self.currency_brl.save()
        transaction2 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000)
        
        self.currency_brl.price_brl = 12.76
        self.currency_brl.price_usd = 25.52
        self.currency_brl.save()
        transaction3 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000)
        
        self.currency_brl.price_brl = 18.34
        self.currency_brl.price_usd = 36.68
        self.currency_brl.save()
        transaction4 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000)

        # Agora, modificamos a transaction3
        self.currency_brl.price_brl = 21.85
        self.currency_brl.price_usd = 43.70
        self.currency_brl.save()
        transaction3.transaction_amount = 1500
        transaction3.save()

        # Calculamos o preço médio esperado após a modificação. O preço médio é a soma do custo de todas as transações dividido pelo número total de ações.
        total_cost_brl = (transaction1.transaction_amount * transaction1.price_brl +
                        transaction2.transaction_amount * transaction2.price_brl +
                        transaction3.transaction_amount * transaction3.price_brl +
                        transaction4.transaction_amount * transaction4.price_brl)

        total_cost_usd = (transaction1.transaction_amount * transaction1.price_usd +
                        transaction2.transaction_amount * transaction2.price_usd +
                        transaction3.transaction_amount * transaction3.price_usd +
                        transaction4.transaction_amount * transaction4.price_usd)

        total_shares = (transaction1.transaction_amount +
                        transaction2.transaction_amount +
                        transaction3.transaction_amount +
                        transaction4.transaction_amount)

        expected_average_price_brl = total_cost_brl / total_shares
        expected_average_price_usd = total_cost_usd / total_shares

        # Verificamos se o preço médio armazenado no PortfolioInvestment corresponde ao preço médio esperado após a modificação da transaction3.
        portfolio_investment = PortfolioInvestment.objects.get(id=transaction4.portfolio_investment.id)
        self.assertEqual(portfolio_investment.share_average_price_brl, expected_average_price_brl)
        self.assertEqual(portfolio_investment.share_average_price_usd, expected_average_price_usd)

    def test_average_price_calculation_with_edit(self):
        # Primeiro, atualizamos o preço da Currency para cada transação
        price_brl = 5.12
        price_usd = 10.25
        transaction1 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=price_brl, price_usd=price_usd)

        price_brl = 8.14
        price_usd = 16.28
        transaction2 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=price_brl, price_usd=price_usd)

        price_brl = 12.76
        price_usd = 25.52
        transaction3 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=price_brl, price_usd=price_usd)

        price_brl = 18.34
        price_usd = 36.68
        transaction4 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000, price_brl=price_brl, price_usd=price_usd)

        # Agora, modificamos a transaction3
        price_brl = 21.85
        price_usd = 43.70
        transaction3.transaction_amount = 1500
        transaction3.price_brl = price_brl
        transaction3.price_usd = price_usd
        transaction3.save()

        # Calculamos o preço médio esperado após a modificação. O preço médio é a soma do custo de todas as transações dividido pelo número total de ações.
        total_cost_brl = (transaction1.transaction_amount * transaction1.price_brl +
                        transaction2.transaction_amount * transaction2.price_brl +
                        transaction3.transaction_amount * transaction3.price_brl +
                        transaction4.transaction_amount * transaction4.price_brl)

        total_cost_usd = (transaction1.transaction_amount * transaction1.price_usd +
                        transaction2.transaction_amount * transaction2.price_usd +
                        transaction3.transaction_amount * transaction3.price_usd +
                        transaction4.transaction_amount * transaction4.price_usd)

        total_shares = (transaction1.transaction_amount +
                        transaction2.transaction_amount +
                        transaction3.transaction_amount +
                        transaction4.transaction_amount)

        expected_average_price_brl = total_cost_brl / total_shares
        expected_average_price_usd = total_cost_usd / total_shares

        # Verificamos se o preço médio armazenado no PortfolioInvestment corresponde ao preço médio esperado após a modificação da transaction3.
        portfolio_investment = PortfolioInvestment.objects.get(id=transaction4.portfolio_investment.id)
        self.assertEqual(portfolio_investment.share_average_price_brl, expected_average_price_brl)
        self.assertEqual(portfolio_investment.share_average_price_usd, expected_average_price_usd)

class CurrencyTransferTest(TestCase):
    def setUp(self):
        self.currency_brl = Currency.objects.create(ticker='BRL', price_brl=1, price_usd=0.20)
        self.currency_usd = Currency.objects.create(ticker='USD', price_brl=5, price_usd=1)
        # br brokers
        self.broker_banco_brasil= Broker.objects.create(name='Banco do Brasil', main_currency=self.currency_brl, slug='banco-do-brasil')
        self.broker_itau= Broker.objects.create(name='Itau', main_currency=self.currency_brl, slug='itau')
        # us brokers
        self.broker_avenue= Broker.objects.create(name='Avenue', main_currency=self.currency_usd, slug='avenue')
        self.broker_inter= Broker.objects.create(name='Inter', main_currency=self.currency_usd, slug='inter')

        # Configuração inicial. Criamos os objetos necessários para os testes.
        self.category = Category.objects.create(name='Test Category')
        self.subcategory = SubCategory.objects.create(name='Test SubCategory')
        self.asset_brl = CurrencyHolding.objects.create(ticker='BRL', category=self.category, subcategory=self.subcategory, currency=self.currency_brl, price_brl=1, price_usd=0.20)
        self.asset_usd = CurrencyHolding.objects.create(ticker='USD', category=self.category, subcategory=self.subcategory, currency=self.currency_usd, price_brl=5, price_usd=1)

        # Cria um usuário para ser o proprietário do portfolio
        self.user = User.objects.create_user(username='testuser', password='12345')
        # Cria um broker para ser usado nas trades

        self.portfolio = Portfolio.objects.create(name='Test Portfolio', owner=self.user)


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


class AssetTransactionTest(TestCase):
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




        
