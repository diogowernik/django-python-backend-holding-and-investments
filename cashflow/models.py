from django.db import models
from brokers.models import Broker
from portfolios.models import Portfolio, PortfolioInvestment
from investments.models import CurrencyHolding
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import datetime
from timewarp.models import CurrencyHistoricalPrice
from django.apps import apps
from django.db.models import Sum

class CurrencyTransaction(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, default=11)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, default=2)
    transaction_type = models.CharField(max_length=50, choices=(('deposit', 'deposit'), ('withdraw', 'withdraw')), default='deposit')
    transaction_amount = models.FloatField(default=0)
    transaction_date = models.DateTimeField(default=timezone.now)
    price_brl = models.FloatField(null=True, blank=True)
    price_usd = models.FloatField(null=True, blank=True)

    portfolio_investment = models.ForeignKey(PortfolioInvestment, on_delete=models.CASCADE, blank=True, null=True)
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if the object is new

        self.set_prices()
        self.set_portfolio_investment()
        super().save(*args, **kwargs)  # Save the object
        self.process_transaction(is_new)

    def set_prices(self):
        self.set_price('BRL', 'price_brl')
        self.set_price('USD', 'price_usd')

    def set_price(self, currency_ticker, price_attribute):
        if getattr(self, price_attribute) is None:
            if self.broker.main_currency.ticker == currency_ticker:
                setattr(self, price_attribute, 1)
            else:
                today = datetime.today().date()  # Mudando para usar apenas a data, removendo o tempo.
                transaction_date = self.transaction_date
                if isinstance(transaction_date, str):
                    transaction_date = datetime.strptime(transaction_date, '%Y-%m-%d').date()  # Converte para datetime.date

                # Checa se transaction_date já é um datetime.date ou se precisa de conversão
                if transaction_date == today:
                    setattr(self, price_attribute, getattr(self.broker.main_currency, price_attribute))
                elif transaction_date < today:
                    self.set_historical_price(currency_ticker, price_attribute, transaction_date)

    # set_historical_price for set_price
    def set_historical_price(self, currency_ticker, price_attribute, transaction_date):
        currency_historical_price = CurrencyHistoricalPrice.objects.filter(
            currency_pair=f'{self.broker.main_currency.ticker}{currency_ticker}',
            date__lte=transaction_date
        ).latest('date')
        if currency_historical_price:
            setattr(self, price_attribute, currency_historical_price.close)
        else:
            raise ValidationError(f'Não foi possível encontrar o preço do ativo {currency_ticker} na data {transaction_date}')

    def set_portfolio_investment(self):
        asset = CurrencyHolding.objects.get(currency=self.broker.main_currency)
        self.portfolio_investment, _ = PortfolioInvestment.objects.get_or_create(
            portfolio=self.portfolio,
            broker=self.broker,
            asset=asset
        )

    def process_transaction(self, is_new):
        transaction_calculation, _ = CurrencyTransactionCalculation.objects.get_or_create(portfolio_investment=self.portfolio_investment)
        transaction_calculation.process_transaction(transaction_date=self.transaction_date, is_new=is_new)
        transaction_calculation.save()

    @transaction.atomic
    def delete(self, *args, **kwargs):
        self.adjust_portfolio_investment()
        self.reprocess_transaction()
        super().delete(*args, **kwargs)

    def adjust_portfolio_investment(self):
        if self.transaction_type == 'deposit':
            self.portfolio_investment.shares_amount -= self.transaction_amount
        elif self.transaction_type == 'withdraw':
            self.portfolio_investment.shares_amount += self.transaction_amount
        self.portfolio_investment.save()

    def reprocess_transaction(self):
        try:
            transaction_calculation = CurrencyTransactionCalculation.objects.get(portfolio_investment=self.portfolio_investment)
            transaction_calculation.process_transaction(transaction_date=self.transaction_date, transaction_id=self.id)
        except CurrencyTransactionCalculation.DoesNotExist:
            pass

    class Meta:
        ordering = ['-transaction_date']
        verbose_name_plural = '  Depósitos e Saques'

    def __str__(self):
        return f'{self.transaction_type} {self.transaction_amount} {self.broker.main_currency.ticker}'

class CurrencyTransactionCalculation(models.Model):
    portfolio_investment = models.OneToOneField(PortfolioInvestment, on_delete=models.CASCADE)
    share_average_price_brl = models.FloatField(default=0)
    share_average_price_usd = models.FloatField(default=0)

    def process_transaction(self, transaction_date, is_new=False, transaction_id=None):
        transactions = self.get_transactions(transaction_id)
        total_brl, total_usd, total_shares = self.calculate_totals(transactions)
        self.update_average_prices(total_brl, total_usd, total_shares)
        self.update_portfolio_investment(total_brl, total_usd, total_shares)

    def get_transactions(self, transaction_id):
        return CurrencyTransaction.objects.filter(portfolio_investment=self.portfolio_investment).exclude(id=transaction_id).order_by('transaction_date')

    def calculate_totals(self, transactions):
        total_brl = 0
        total_usd = 0
        total_shares = 0

        for transaction in transactions:
            if transaction.transaction_type == 'deposit':
                total_brl += transaction.transaction_amount * transaction.price_brl
                total_usd += transaction.transaction_amount * transaction.price_usd
                total_shares += transaction.transaction_amount
            elif transaction.transaction_type == 'withdraw':
                total_brl -= transaction.transaction_amount * transaction.price_brl
                total_usd -= transaction.transaction_amount * transaction.price_usd
                total_shares -= transaction.transaction_amount
        
        return total_brl, total_usd, total_shares

    def update_average_prices(self, total_brl, total_usd, total_shares):
        self.share_average_price_brl = total_brl / total_shares if total_shares != 0 else 0
        self.share_average_price_usd = total_usd / total_shares if total_shares != 0 else 0

    def update_portfolio_investment(self, total_brl, total_usd, total_shares):
        portfolio_investment = self.portfolio_investment
        portfolio_investment.share_average_price_brl = self.share_average_price_brl
        portfolio_investment.share_average_price_usd = self.share_average_price_usd
        portfolio_investment.total_cost_brl = total_brl
        portfolio_investment.total_cost_usd = total_usd
        portfolio_investment.shares_amount = total_shares
        portfolio_investment.total_today_brl = total_shares * portfolio_investment.asset.price_brl
        portfolio_investment.total_today_usd = total_shares * portfolio_investment.asset.price_usd
        portfolio_investment.save()

# Transferência de moedas entre brokers mesma moeda. Ex: Transferir USD do Interactive Brokers para o TD Ameritrade
class CurrencyTransfer(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, default=11)
    from_broker = models.ForeignKey(Broker, related_name='transfer_from', on_delete=models.CASCADE, default=1)
    to_broker = models.ForeignKey(Broker, related_name='transfer_to', on_delete=models.CASCADE, default=2)
    transfer_amount = models.FloatField()
    transfer_date = models.DateField(default=timezone.now)

    # Adicione campos ForeignKey para as transações
    from_transaction = models.ForeignKey(CurrencyTransaction, related_name='from_transfers', on_delete=models.SET_NULL, null=True, blank=True)
    to_transaction = models.ForeignKey(CurrencyTransaction, related_name='to_transfers', on_delete=models.SET_NULL, null=True, blank=True)

    def create_transactions(self):
        self.from_transaction = CurrencyTransaction.objects.create(
            portfolio=self.portfolio,
            broker=self.from_broker,
            transaction_type='withdraw',
            transaction_amount=self.transfer_amount,
            transaction_date=self.transfer_date,
        )
        self.to_transaction = CurrencyTransaction.objects.create(
            portfolio=self.portfolio,
            broker=self.to_broker,
            transaction_type='deposit',
            transaction_amount=self.transfer_amount,
            transaction_date=self.transfer_date,
        )

    def update_transactions(self):
        self.from_transaction.transaction_amount = self.transfer_amount
        self.from_transaction.save()
        self.to_transaction.transaction_amount = self.transfer_amount
        self.to_transaction.save()

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.full_clean()  # Isto irá chamar o método clean

        # Se for uma edição, atualize as transações existentes
        if self.pk is not None and self.from_transaction and self.to_transaction:
            self.update_transactions()
        # Caso contrário, crie novas transações
        else:
            self.create_transactions()

        super().save(*args, **kwargs)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        if self.from_transaction:
            self.from_transaction.delete()
        if self.to_transaction:
            self.to_transaction.delete()
        super().delete(*args, **kwargs)
    
    def clean(self):
        if self.from_broker == self.to_broker:
            raise ValidationError("Os brokers de origem e destino devem ser diferentes.")
    
    class Meta:
        ordering = ['-transfer_date']
        verbose_name_plural = ' Transferências mesma moeda'


# Transferência de moedas entre brokers internacionais. Ex: Transferir USD do Banco do Brasil para o TD Ameritrade
class InternationalCurrencyTransfer(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, default=11)
    from_broker = models.ForeignKey(Broker, related_name='international_transfer_from', on_delete=models.CASCADE, default=1)
    to_broker = models.ForeignKey(Broker, related_name='intternational_transfer_to', on_delete=models.CASCADE, default=2)
    from_transfer_amount = models.FloatField(default=0)  # Quantidade na moeda original
    to_transfer_amount = models.FloatField(editable=False, default=0) # Quantidade na moeda de destino, após a conversão
    transfer_fee = models.FloatField(default=0)  # Taxa de transferência cobrada pelo corretor
    exchange_rate = models.FloatField(default=0)  # Taxa de câmbio usada na transferência
    transfer_date = models.DateField(default=timezone.now)

    from_transaction = models.ForeignKey(CurrencyTransaction, related_name='from_international_transfers', on_delete=models.SET_NULL, null=True, blank=True)
    to_transaction = models.ForeignKey(CurrencyTransaction, related_name='to_international_transfers', on_delete=models.SET_NULL, null=True, blank=True)

    def calculate_to_transfer_amount(self):
        # Calcula o to_transfer_amount baseado no from_transfer_amount e na taxa de câmbio
        self.to_transfer_amount = self.from_transfer_amount / self.exchange_rate

    def create_transactions(self):
        self.from_transaction = CurrencyTransaction.objects.create(
            portfolio=self.portfolio,
            broker=self.from_broker,
            transaction_type='withdraw',
            transaction_amount=self.from_transfer_amount,
            transaction_date=self.transfer_date,
        )
        self.to_transaction = CurrencyTransaction.objects.create(
            portfolio=self.portfolio,
            broker=self.to_broker,
            transaction_type='deposit',
            transaction_amount=self.to_transfer_amount,
            transaction_date=self.transfer_date,
        )

    def update_transactions(self):
        self.from_transaction.transaction_amount = self.from_transfer_amount
        self.from_transaction.save()
        self.to_transaction.transaction_amount = self.to_transfer_amount
        self.to_transaction.save()

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.full_clean()  # Isto irá chamar o método clean
        self.calculate_to_transfer_amount()

        # Se for uma edição, atualize as transações existentes
        if self.pk is not None and self.from_transaction and self.to_transaction:
            self.update_transactions()
        # Caso contrário, crie novas transações
        else:
            self.create_transactions()

        super().save(*args, **kwargs)
    
    @transaction.atomic
    def delete(self, *args, **kwargs):
        if self.from_transaction:
            self.from_transaction.delete()
        if self.to_transaction:
            self.to_transaction.delete()
        super().delete(*args, **kwargs)
    
    def clean(self):
        if self.from_broker == self.to_broker:
            raise ValidationError("Os brokers de origem e destino devem ser diferentes.")
        
        if self.from_broker.main_currency == self.to_broker.main_currency:
            raise ValidationError("A moeda principal dos brokers de origem e destino devem ser diferentes.")
        
        if self.exchange_rate <= 0:
            raise ValidationError("A taxa de câmbio deve ser um número positivo.")
        
        if self.from_transfer_amount <= 0:
            raise ValidationError("A quantidade de moeda a ser transferida deve ser maior que zero.")
        
    class Meta:
        ordering = ['-transfer_date']
        verbose_name_plural = 'Transferências Internacionais'



        

            


