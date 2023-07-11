from django.db import models
from brokers.models import Broker, CurrencyHistoricalPrice
from portfolios.models import Portfolio, PortfolioInvestment
from investments.models import Asset, CurrencyHolding, AssetHistoricalPrice
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from datetime import datetime
from django.apps import apps

class CurrencyTransaction(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, default=11)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, default=2)
    transaction_type = models.CharField(max_length=50, choices=(('deposit', 'Deposit'), ('withdraw', 'Withdraw')), default='deposit')
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

    def set_price(self, currency_ticker, price_attribute):
        if getattr(self, price_attribute) is None:
            if self.broker.main_currency.ticker == currency_ticker:
                setattr(self, price_attribute, 1)
            else:
                today = datetime.today().strftime('%Y-%m-%d')
                transaction_date = self.transaction_date.strftime('%Y-%m-%d')
                if transaction_date == today:
                    setattr(self, price_attribute, getattr(self.broker.main_currency, price_attribute))
                elif transaction_date < today:
                    currency_historical_price = CurrencyHistoricalPrice.objects.filter(
                        currency_pair=f'{self.broker.main_currency.ticker}{currency_ticker}',
                        date__lte=transaction_date
                    ).latest('date')
                    if currency_historical_price:
                        setattr(self, price_attribute, currency_historical_price.price)
                    else:
                        raise ValidationError(f'Não foi possível encontrar o preço do ativo {currency_ticker} na data {transaction_date}')

    def set_prices(self):
        self.set_price('BRL', 'price_brl')
        self.set_price('USD', 'price_usd')

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
        self.recalculate_averages()
        super().delete(*args, **kwargs)

    def adjust_portfolio_investment(self):
        if self.transaction_type == 'deposit':
            self.portfolio_investment.shares_amount -= self.transaction_amount
        elif self.transaction_type == 'withdraw':
            self.portfolio_investment.shares_amount += self.transaction_amount
        self.portfolio_investment.save()

    def recalculate_averages(self):
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

# Compra e venda de ativos (Reit, BrStocks, Fii, Stocks)
class AssetTransaction(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, default=11)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, default=1)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, default=1)
    transaction_type = models.CharField(max_length=50, choices=(('buy', 'Buy'), ('sell', 'Sell')), default='buy')
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
        self.create_or_update_currency_transaction()
        self.process_transaction(is_new)

    def set_price(self, asset_ticker, target_currency):
        price_attribute = f'price_{target_currency.lower()}'
        if getattr(self, price_attribute) is None:
            today = datetime.today().strftime('%Y-%m-%d')
            transaction_date = self.transaction_date.strftime('%Y-%m-%d')
            if transaction_date == today:
                setattr(self, price_attribute, getattr(self.asset, price_attribute))
            elif transaction_date < today:
                try:
                    asset_historical_price = AssetHistoricalPrice.objects.get(
                        asset__ticker=asset_ticker, 
                        date=transaction_date
                    )

                    # Verifique a moeda do preço histórico
                    historical_price_currency = asset_historical_price.currency

                    if historical_price_currency == target_currency:
                        setattr(self, price_attribute, asset_historical_price.close)
                    else:
                        # Converta o preço histórico para a moeda alvo
                        currency_historical_price = CurrencyHistoricalPrice.objects.filter(
                            currency_pair=f'{historical_price_currency}{target_currency}',
                            date__lte=transaction_date
                        ).latest('date')

                        if currency_historical_price:
                            converted_price = asset_historical_price.close * currency_historical_price.close
                            setattr(self, price_attribute, converted_price)
                        else:
                            raise ValidationError(f'Não foi possível encontrar a taxa de câmbio de {historical_price_currency} para {target_currency} na data {transaction_date}')

                except ObjectDoesNotExist:
                    raise ValidationError(f'Não foi possível encontrar o preço do ativo {asset_ticker} na data {transaction_date}')

    def set_prices(self):
        self.set_price(self.asset.ticker, 'BRL') # price_brl
        self.set_price(self.asset.ticker, 'USD') # price_usd



    def set_portfolio_investment(self):
        self.portfolio_investment, _ = PortfolioInvestment.objects.get_or_create(
            portfolio=self.portfolio,
            broker=self.broker,
            asset=self.asset
        )

    def create_or_update_currency_transaction(self):
        currency_transaction_type = 'withdraw' if self.transaction_type == 'buy' else 'deposit'
        currency_transaction_amount = self.get_currency_transaction_amount()

        currency_transaction, created = CurrencyTransaction.objects.get_or_create(
            portfolio=self.portfolio,
            broker=self.broker,
            transaction_date=self.transaction_date,
            defaults={
                'transaction_type': currency_transaction_type,
                'transaction_amount': currency_transaction_amount,
                'price_brl': self.price_brl,
                'price_usd': self.price_usd,
            }
        )

        if not created:
            currency_transaction.transaction_type = currency_transaction_type
            currency_transaction.transaction_amount = currency_transaction_amount
            currency_transaction.price_brl = self.price_brl
            currency_transaction.price_usd = self.price_usd
            currency_transaction.save()

    def get_currency_transaction_amount(self):
        if self.broker.main_currency.ticker == 'BRL':
            return self.transaction_amount * self.price_brl
        elif self.broker.main_currency.ticker == 'USD':
            return self.transaction_amount * self.price_usd

    def process_transaction(self, is_new):
        transaction_calculation, _ = AssetTransactionCalculation.objects.get_or_create(portfolio_investment=self.portfolio_investment)
        transaction_calculation.transaction_date = self.transaction_date
        transaction_calculation.last_transaction = self
        transaction_calculation.process_transaction(transaction_date=self.transaction_date, is_new=is_new)
        transaction_calculation.save()

    @transaction.atomic  
    def delete(self, *args, **kwargs):
        self.adjust_portfolio_investment()
        self.recalculate_averages()
        self.delete_currency_transaction()
        super().delete(*args, **kwargs)    

    def adjust_portfolio_investment(self):
        if self.transaction_type == 'buy':
            self.portfolio_investment.shares_amount -= self.transaction_amount
        elif self.transaction_type == 'sell':
            self.portfolio_investment.shares_amount += self.transaction_amount
        self.portfolio_investment.save()

    def recalculate_averages(self):
        try:
            transaction_calculation = AssetTransactionCalculation.objects.get(portfolio_investment=self.portfolio_investment)
            transaction_calculation.process_transaction(transaction_date=self.transaction_date, transaction_id=self.id)
        except AssetTransactionCalculation.DoesNotExist:
            pass

    def delete_currency_transaction(self):
        try:
            currency_transaction = CurrencyTransaction.objects.get(
                portfolio=self.portfolio,
                broker=self.broker,
                transaction_date=self.transaction_date
            )
            currency_transaction.delete()
        except CurrencyTransaction.DoesNotExist:
            pass
    
    class Meta:
        ordering = ['-transaction_date']
        verbose_name = ' Compra e Venda de Ativo'
        verbose_name_plural = ' Compra e Venda de Ativos'

    def __str__(self):
        return f'{self.asset.ticker} - {self.transaction_date.strftime("%d/%m/%Y")}'

class AssetTransactionCalculation(models.Model):
    portfolio_investment = models.OneToOneField(PortfolioInvestment, on_delete=models.CASCADE)
    last_transaction = models.ForeignKey(AssetTransaction, null=True, blank=True, on_delete=models.SET_NULL) # SET_NULL importante, não queremos deletar o objeto pois ele representa um estado.
    share_average_price_brl = models.FloatField(default=0)
    share_average_price_usd = models.FloatField(default=0)
    trade_profit_brl = models.FloatField(default=0)
    trade_profit_usd = models.FloatField(default=0)
    total_shares = models.FloatField(default=0)
    total_brl = models.FloatField(default=0)
    total_usd = models.FloatField(default=0)
    transaction_date = models.DateTimeField(default=timezone.now)

    def process_transaction(self, transaction_date, is_new=False, transaction_id=None): 
        transactions = self.get_transactions(transaction_id)
        total_brl, total_usd, total_shares, trade_profit_brl, trade_profit_usd, share_avg_price_brl, share_avg_price_usd = self.calculate_totals_and_profits(transactions)
        transactions_until_date = self.get_transactions_until_date(transaction_date)
        total_brl_until_date, total_usd_until_date, total_shares_until_date, _, _, _, _ = self.calculate_totals_and_profits(transactions_until_date)
        self.update_self_values(total_brl, total_usd, total_shares, trade_profit_brl, trade_profit_usd)
        self.create_transaction_history(total_brl_until_date, total_usd_until_date, total_shares_until_date, share_avg_price_brl, share_avg_price_usd)
        self.update_portfolio_investment(total_brl, total_usd, total_shares)

    def get_transactions(self, transaction_id):
        return AssetTransaction.objects.filter(portfolio_investment=self.portfolio_investment).exclude(id=transaction_id).order_by('transaction_date')

    def get_transactions_until_date(self, transaction_date):
        return AssetTransaction.objects.filter(portfolio_investment=self.portfolio_investment, transaction_date__lte=transaction_date).order_by('transaction_date')

    def calculate_totals_and_profits(self, transactions):
        total_brl = 0
        total_usd = 0
        total_shares = 0
        trade_profit_brl = 0
        trade_profit_usd = 0
        for transaction in transactions:
            if transaction.transaction_type == 'buy':
                total_brl += transaction.transaction_amount * transaction.price_brl
                total_usd += transaction.transaction_amount * transaction.price_usd
                total_shares += transaction.transaction_amount
            elif transaction.transaction_type == 'sell':
                sell_brl = transaction.transaction_amount * transaction.price_brl
                sell_usd = transaction.transaction_amount * transaction.price_usd
                cost_brl = transaction.transaction_amount * self.share_average_price_brl
                cost_usd = transaction.transaction_amount * self.share_average_price_usd
                
                trade_profit_brl += sell_brl - cost_brl
                trade_profit_usd += sell_usd - cost_usd
                
                total_brl -= cost_brl
                total_usd -= cost_usd
                total_shares -= transaction.transaction_amount

        share_avg_price_brl_until_date = total_brl / total_shares if total_shares != 0 else 0
        share_avg_price_usd_until_date = total_usd / total_shares if total_shares != 0 else 0

        return total_brl, total_usd, total_shares, trade_profit_brl, trade_profit_usd, share_avg_price_brl_until_date, share_avg_price_usd_until_date

    def update_self_values(self, total_brl, total_usd, total_shares, trade_profit_brl, trade_profit_usd):
        self.share_average_price_brl = total_brl / total_shares if total_shares != 0 else 0
        self.share_average_price_usd = total_usd / total_shares if total_shares != 0 else 0
        self.trade_profit_brl = trade_profit_brl
        self.trade_profit_usd = trade_profit_usd
        self.total_brl = total_brl
        self.total_usd = total_usd
        self.total_shares = total_shares

    def create_transaction_history(self, total_brl_until_date, total_usd_until_date, total_shares_until_date, share_avg_price_brl_until_date, share_avg_price_usd_until_date): 
        TransactionsHistory.objects.create(
            portfolio_investment=self.portfolio_investment,
            transaction=self.last_transaction,
            share_average_price_brl= share_avg_price_brl_until_date,
            share_average_price_usd= share_avg_price_usd_until_date,
            total_shares=total_shares_until_date,
            total_brl=total_brl_until_date,
            total_usd=total_usd_until_date,
            transaction_date=self.transaction_date
        )

    def update_portfolio_investment(self, total_brl, total_usd, total_shares):
        portfolio_investment = self.portfolio_investment
        portfolio_investment.share_average_price_brl = self.share_average_price_brl
        portfolio_investment.share_average_price_usd = self.share_average_price_usd
        portfolio_investment.total_cost_brl = total_brl
        portfolio_investment.total_cost_usd = total_usd
        portfolio_investment.shares_amount = total_shares
        portfolio_investment.trade_profit_brl = self.trade_profit_brl
        portfolio_investment.trade_profit_usd = self.trade_profit_usd
        portfolio_investment.total_today_brl = total_shares * portfolio_investment.asset.price_brl
        portfolio_investment.total_today_usd = total_shares * portfolio_investment.asset.price_usd
        portfolio_investment.save()

    class Meta:
        ordering = ['-transaction_date']
        verbose_name = ' Compra e Venda / Calculos'
        verbose_name_plural = ' Compras e Vendas / Calculos'

# Histórico de Preço Médio do Ativo, Total de Ações, Total em BRL e Total em USD, Transação
class TransactionsHistory(models.Model):
    portfolio_investment = models.ForeignKey(PortfolioInvestment, on_delete=models.CASCADE)
    transaction = models.ForeignKey(AssetTransaction, on_delete=models.CASCADE)
    share_average_price_brl = models.FloatField()
    share_average_price_usd = models.FloatField()
    total_shares = models.FloatField()
    total_brl = models.FloatField()
    total_usd = models.FloatField()
    transaction_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.create_portfolio_dividend()
        super().save(*args, **kwargs)

    def create_portfolio_dividend(self):
        Dividend = apps.get_model('dividends', 'Dividend')
        PortfolioDividend = apps.get_model('dividends', 'PortfolioDividend')
        dividends = Dividend.objects.filter(record_date__gte=self.transaction_date)

        for dividend in dividends:
                # Crie PortfolioDividend através da função centralizada
                PortfolioDividend.create(self, dividend)  # foi alterado aqui

    class Meta:
        ordering = ['-transaction_date']
        verbose_name = ' Compra e Venda / Histórico'
        verbose_name_plural = ' Compras e Vendas / Histórico'

# entrada de dinheiro na carteira, como salário ou renda extra, criará uma transação de moeda (CurrencyTransaction) Deposit
class Income(CurrencyTransaction):
    transaction_category = models.CharField(
        max_length=255,
        choices=(
            ('Renda Ativa', 'Renda Ativa'),  # Salário Principal, 
            ('Renda Extra', 'Renda Extra'),  # Venda de algo, Freelancer, Autônomo, etc
            ('Renda Passiva', 'Renda Passiva'),  # Dividendos, Aluguéis, será que junto aqui?
            ('Outros', 'Outros'),
        ),
        default='Renda Ativa'
    )
    # Será que vale a pena criar um model para categorias de renda? Acho que não, mas talvez seja interessante
    
    def save(self, *args, **kwargs):
        self.transaction.transaction_type = 'deposit'
        self.transaction.save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Receita'
        verbose_name_plural = 'Receitas'
        
    def __str__(self):
        return f"{self.description} | {self.transaction.transaction_amount} | {self.transaction.broker.main_currency}"
    
class Expense(CurrencyTransaction):
    transaction_category = models.CharField(
        max_length=255,
        choices=(
            ('Cartão de Crédito', 'Cartão de Crédito'),  # Mercado, Farmácia, etc
            ('Casa', 'Casa'),  # Aluguel, Condomínio, Luz, Água, Internet, etc
            ('Manutenção de Ativos', 'Manutenção de Ativos'),  # Condominio, IPTU de imóveis, Taxas, etc
            ('Imposto', 'Imposto'),  # IR, IOF, etc
        ),
        default='Cartão de Crédito'
    )
    # Será que vale a pena criar um model para categorias de despesa? Acho que não, mas talvez seja interessante
    # Será que vale a pena um campo description? Acho que não, mas talvez seja interessante
    
    def save(self, *args, **kwargs):
        self.transaction.transaction_type = 'withdraw'
        self.transaction.save()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Despesa'
        verbose_name_plural = 'Despesas'

    def __str__(self):
        return f"{self.description} - {self.transaction.transaction_amount}"



