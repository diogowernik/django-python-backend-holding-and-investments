from django.test import TestCase
from portfolios.models import PortfolioInvestment,Portfolio
from investments.models import CurrencyHolding
from brokers.models import Broker, Currency 
from cashflow.models import CurrencyTransaction
from categories.models import Category, SubCategory
from django.contrib.auth.models import User


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
        transaction1 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction1.portfolio_investment.id).shares_amount, 1000)

        transaction2 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction2.portfolio_investment.id).shares_amount, 2000)

        transaction3 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction3.portfolio_investment.id).shares_amount, 3000)

        transaction4 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction4.portfolio_investment.id).shares_amount, 4000)

    def test_usd_currency_transactions(self):
        # A partir daqui, você pode usar self.broker_avenue e self.portfolio para criar suas transações
        transaction1 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_avenue, transaction_type='deposit', transaction_amount=1000)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction1.portfolio_investment.id).shares_amount, 1000)

        transaction2 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_avenue, transaction_type='deposit', transaction_amount=1000)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction2.portfolio_investment.id).shares_amount, 2000)

        transaction3 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_avenue, transaction_type='deposit', transaction_amount=1000)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction3.portfolio_investment.id).shares_amount, 3000)

        transaction4 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_avenue, transaction_type='deposit', transaction_amount=1000)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction4.portfolio_investment.id).shares_amount, 4000)

    def test_brl_currency_withdraw(self):
        # Primeiro, criamos duas transações de depósito, para que tenhamos algo para retirar.
        CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=2000)

        # A partir daqui, você pode usar self.broker, self.currency e self.portfolio para criar suas transações
        transaction1 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='withdraw', transaction_amount=500)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction1.portfolio_investment.id).shares_amount, 1500)

        transaction2 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='withdraw', transaction_amount=500)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction2.portfolio_investment.id).shares_amount, 1000)

    def test_edit_first_brl_currency_transaction(self):
        # Primeiro, criamos quatro transações de depósito.
        transaction1 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000)
        transaction2 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000)
        transaction3 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000)
        transaction4 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction4.portfolio_investment.id).shares_amount, 4000)

        # Agora, editamos a primeira transação e verificamos se a quantidade de ações foi atualizada corretamente.
        transaction1.transaction_amount = 2000
        transaction1.save()
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction1.portfolio_investment.id).shares_amount, 5000)

    def test_edit_first_brl_currency_transaction_with_two_brokers(self):
        # Primeiro, criamos quatro transações de depósito.
        transaction1 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000)
        transaction2 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000)
        
        # Terceira transação é feita com uma broker diferente.
        transaction3 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_itau, transaction_type='deposit', transaction_amount=1000)

        transaction4 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction4.portfolio_investment.id).shares_amount, 3000)

        # Agora, editamos a primeira transação e verificamos se a quantidade de ações foi atualizada corretamente.
        transaction1.transaction_amount = 2000
        transaction1.save()
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction1.portfolio_investment.id).shares_amount, 4000)

        # Também verificamos se a quantidade de ações na broker_itau está correta.
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction3.portfolio_investment.id).shares_amount, 1000)

    def test_delete_brl_currency_transaction(self):
        # Primeiro, criamos duas transações de depósito.
        transaction1 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000)
        transaction2 = CurrencyTransaction.objects.create(portfolio=self.portfolio, broker=self.broker_banco_brasil, transaction_type='deposit', transaction_amount=1000)
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction2.portfolio_investment.id).shares_amount, 2000)

        # Agora, deletamos a primeira transação e verificamos se a quantidade de ações foi atualizada corretamente.
        transaction1.delete()
        self.assertEqual(PortfolioInvestment.objects.get(id=transaction2.portfolio_investment.id).shares_amount, 1000)

    def test_average_price_calculation_three_transactions(self):
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

        # Calculamos o preço médio esperado. O preço médio é a soma do custo de todas as transações dividido pelo número total de ações.
        total_cost_brl = (transaction1.transaction_amount * transaction1.broker.main_currency.price_brl +
                        transaction2.transaction_amount * transaction2.broker.main_currency.price_brl +
                        transaction3.transaction_amount * transaction3.broker.main_currency.price_brl)

        total_cost_usd = (transaction1.transaction_amount * transaction1.broker.main_currency.price_usd +
                        transaction2.transaction_amount * transaction2.broker.main_currency.price_usd +
                        transaction3.transaction_amount * transaction3.broker.main_currency.price_usd)

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

        # Agora, deletamos a transação 2
        transaction2.delete()

        # Calculamos o preço médio esperado após a deleção. O preço médio é a soma do custo das transações restantes dividido pelo número total de ações restantes.
        total_cost_brl = (transaction1.transaction_amount * transaction1.broker.main_currency.price_brl +
                        transaction3.transaction_amount * transaction3.broker.main_currency.price_brl +
                        transaction4.transaction_amount * transaction4.broker.main_currency.price_brl)

        total_cost_usd = (transaction1.transaction_amount * transaction1.broker.main_currency.price_usd +
                        transaction3.transaction_amount * transaction3.broker.main_currency.price_usd +
                        transaction4.transaction_amount * transaction4.broker.main_currency.price_usd)

        total_shares = (transaction1.transaction_amount +
                        transaction3.transaction_amount +
                        transaction4.transaction_amount)

        expected_average_price_brl = total_cost_brl / total_shares
        expected_average_price_usd = total_cost_usd / total_shares

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
        total_cost_brl = (transaction1.transaction_amount * transaction1.broker.main_currency.price_brl +
                        transaction2.transaction_amount * transaction2.broker.main_currency.price_brl +
                        transaction3.transaction_amount * transaction3.broker.main_currency.price_brl +
                        transaction4.transaction_amount * transaction4.broker.main_currency.price_brl)

        total_cost_usd = (transaction1.transaction_amount * transaction1.broker.main_currency.price_usd +
                        transaction2.transaction_amount * transaction2.broker.main_currency.price_usd +
                        transaction3.transaction_amount * transaction3.broker.main_currency.price_usd +
                        transaction4.transaction_amount * transaction4.broker.main_currency.price_usd)

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
