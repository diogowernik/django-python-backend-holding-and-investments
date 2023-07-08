from django.db import models
from brokers.models import Broker
from portfolios.models import Portfolio, PortfolioInvestment
from investments.models import Asset, CurrencyHolding
from django.utils import timezone
from investments.utils.get_currency_price import get_exchange_rate
from django.db import transaction
from django.core.exceptions import ValidationError

# Deposito e Saque de dinheiro (Mesma moeda do broker)
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
        self.recalculate_average_prices(is_new)

    def set_prices(self):
        self.price_brl = self.get_exchange_rate('BRL')
        self.price_usd = self.get_exchange_rate('USD')

    def get_exchange_rate(self, target_currency):
        if getattr(self.broker.main_currency, 'ticker') == target_currency:
            return 1
        try:
            return get_exchange_rate(self.broker.main_currency.ticker, target_currency, self.transaction_date.strftime('%Y-%m-%d'))
        except:
            return getattr(self.broker.main_currency, f'price_{target_currency.lower()}')

    def set_portfolio_investment(self):
        asset = CurrencyHolding.objects.get(currency=self.broker.main_currency)
        self.portfolio_investment, _ = PortfolioInvestment.objects.get_or_create(
            portfolio=self.portfolio,
            broker=self.broker,
            asset=asset
        )

    def recalculate_average_prices(self, is_new):
        portfolio_average_price, _ = CurrencyAveragePrice.objects.get_or_create(portfolio_investment=self.portfolio_investment)
        portfolio_average_price.recalculate_average(start_date=self.transaction_date, is_new=is_new)
        portfolio_average_price.save()

    @transaction.atomic
    def delete(self, *args, **kwargs):
        # Antes de deletar o objeto, precisamos ajustar a quantidade de ações em portfolio_investment
        if self.transaction_type == 'deposit':
            self.portfolio_investment.shares_amount -= self.transaction_amount
        elif self.transaction_type == 'withdraw':
            self.portfolio_investment.shares_amount += self.transaction_amount
        self.portfolio_investment.save()

        # Em seguida, recalcule as médias
        try:
            portfolio_average_price = CurrencyAveragePrice.objects.get(portfolio_investment=self.portfolio_investment)
            portfolio_average_price.recalculate_average(start_date=self.transaction_date, transaction_id=self.id)
        except CurrencyAveragePrice.DoesNotExist:
            pass

        # Agora, podemos deletar o objeto
        super(CurrencyTransaction, self).delete(*args, **kwargs)

    class Meta:
        ordering = ['-transaction_date']
        verbose_name_plural = 'Depósitos e Saques'

    def __str__(self):
        return f'{self.transaction_type} {self.transaction_amount} {self.broker.main_currency.ticker}'

# Preço Médio, Total Investido, Total Atual (Mesma moeda do broker, calculado em BRL e USD)
class CurrencyAveragePrice(models.Model):
    portfolio_investment = models.OneToOneField(PortfolioInvestment, on_delete=models.CASCADE)
    share_average_price_brl = models.FloatField(default=0)
    share_average_price_usd = models.FloatField(default=0)

    def recalculate_average(self, start_date, is_new=False, transaction_id=None):
        # Obter todas as transações do portfolio_investment, ordenadas por data
        transactions = CurrencyTransaction.objects.filter(portfolio_investment=self.portfolio_investment).exclude(id=transaction_id).order_by('transaction_date')

        # Iniciar total_brl, total_usd, e total_shares com 0
        total_brl = 0
        total_usd = 0
        total_shares = 0

        # Percorrer as transações e recalcular a quantidade total de ações e os totais brl e usd
        for transaction in transactions:
            if transaction.transaction_type == 'deposit':
                total_brl += transaction.transaction_amount * transaction.price_brl
                total_usd += transaction.transaction_amount * transaction.price_usd
                total_shares += transaction.transaction_amount
            elif transaction.transaction_type == 'withdraw':
                total_brl -= transaction.transaction_amount * transaction.price_brl
                total_usd -= transaction.transaction_amount * transaction.price_usd
                total_shares -= transaction.transaction_amount

        # Atualizar os preços médios
        self.share_average_price_brl = total_brl / total_shares if total_shares != 0 else 0
        self.share_average_price_usd = total_usd / total_shares if total_shares != 0 else 0

        # Atualizar o portfolio_investment correspondente
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

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.full_clean()  # Isto irá chamar o método clean
        # Se for uma edição, atualize as transações existentes
        if self.pk is not None and self.from_transaction and self.to_transaction:
            self.from_transaction.transaction_amount = self.transfer_amount
            self.from_transaction.save()
            self.to_transaction.transaction_amount = self.transfer_amount
            self.to_transaction.save()
        # Caso contrário, crie novas transações
        else:
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

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.full_clean()  # Isto irá chamar o método clean
        # Calcula o to_transfer_amount baseado no from_transfer_amount e na taxa de câmbio
        self.to_transfer_amount = self.from_transfer_amount / self.exchange_rate
        # Se for uma edição, atualize as transações existentes
        if self.pk is not None and self.from_transaction and self.to_transaction:
            self.from_transaction.transaction_amount = self.from_transfer_amount
            self.from_transaction.save()
            self.to_transaction.transaction_amount = self.to_transfer_amount
            self.to_transaction.save()
        # Caso contrário, crie novas transações
        else:
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

        if not self.price_brl:
            self.price_brl = self.asset.price_brl
        if not self.price_usd:
            self.price_usd = self.asset.price_usd

        # Find or create a PortfolioInvestment with the correct Portfolio, Broker and Asset
        self.portfolio_investment, _ = PortfolioInvestment.objects.get_or_create(
            portfolio=self.portfolio,
            broker=self.broker,
            asset=self.asset
        )

        # Save the object
        super().save(*args, **kwargs)

        # Create a CurrencyTransaction
            # Determine the transaction_type for the CurrencyTransaction
        if self.transaction_type == 'buy':
            currency_transaction_type = 'withdraw'

        else:  # self.transaction_type == 'sell'
            currency_transaction_type = 'deposit'

        # Determine the transaction_amount for the CurrencyTransaction
        if self.broker.main_currency.ticker == 'BRL':
            currency_transaction_amount = self.transaction_amount * self.price_brl
        elif self.broker.main_currency.ticker == 'USD':
            currency_transaction_amount = self.transaction_amount * self.price_usd

                    # Create the CurrencyTransaction
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


        # Recalculate share_average_price_brl and share_average_price_usd
        portfolio_average_price, _ = AssetAveragePrice.objects.get_or_create(portfolio_investment=self.portfolio_investment)
        portfolio_average_price.transaction_date = self.transaction_date
        portfolio_average_price.last_transaction = self
        portfolio_average_price.recalculate_average(start_date=self.transaction_date, is_new=is_new)
        portfolio_average_price.save()

    @transaction.atomic    
    def delete(self, *args, **kwargs):
        # Antes de deletar o objeto, precisamos ajustar a quantidade de ações em portfolio_investment
        if self.transaction_type == 'buy':
            self.portfolio_investment.shares_amount -= self.transaction_amount
        elif self.transaction_type == 'sell':
            self.portfolio_investment.shares_amount += self.transaction_amount
        self.portfolio_investment.save()

        # Em seguida, recalcule as médias
        try:
            portfolio_average_price = AssetAveragePrice.objects.get(portfolio_investment=self.portfolio_investment)
            portfolio_average_price.recalculate_average(start_date=self.transaction_date, transaction_id=self.id)
        except AssetAveragePrice.DoesNotExist:
            pass  

        # Depois deletar a CurrencyTransaction correspondente
        try:
            currency_transaction = CurrencyTransaction.objects.get(
                portfolio=self.portfolio,
                broker=self.broker,
                transaction_date=self.transaction_date
            )
            currency_transaction.delete()
        except CurrencyTransaction.DoesNotExist:
            pass  

        # Agora, podemos deletar o objeto
        super(AssetTransaction, self).delete(*args, **kwargs)
    
    class Meta:
        ordering = ['-transaction_date']
        verbose_name = 'Compra e Venda de Ativo'
        verbose_name_plural = 'Compra e Venda de Ativos'

# Média de preço de um ativo em um portfolio, Total de lucro/prejuízo, 
# total investido (Mesma moeda do Broker) é criado apenas 1 por portfolio_investment o qual é atualizado a cada compra/venda
# Gera um AssetAverageHistory a cada atualização
class AssetAveragePrice(models.Model):
    portfolio_investment = models.OneToOneField(PortfolioInvestment, on_delete=models.CASCADE)
    last_transaction = models.ForeignKey(AssetTransaction, null=True, blank=True, on_delete=models.SET_NULL) # não deleta o objeto, apenas seta o campo como null
    share_average_price_brl = models.FloatField(default=0)
    share_average_price_usd = models.FloatField(default=0)
    trade_profit_brl = models.FloatField(default=0)
    trade_profit_usd = models.FloatField(default=0)
    total_shares = models.FloatField(default=0)
    total_brl = models.FloatField(default=0)
    total_usd = models.FloatField(default=0)
    transaction_date = models.DateTimeField(default=timezone.now)

    def recalculate_average(self, start_date, is_new=False, transaction_id=None):
        # Get all transactions for this portfolio_investment, ordered by date
        transactions = AssetTransaction.objects.filter(portfolio_investment=self.portfolio_investment).exclude(id=transaction_id).order_by('transaction_date')

        # Initialize total_brl, total_usd, and total_shares with 0
        total_brl = 0
        total_usd = 0
        total_shares = 0
        trade_profit_brl = 0
        trade_profit_usd = 0

        # Go through the transactions and recalculate the total shares and total brl and usd
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

        # Update self values
        self.share_average_price_brl = total_brl / total_shares if total_shares != 0 else 0
        self.share_average_price_usd = total_usd / total_shares if total_shares != 0 else 0
        self.trade_profit_brl = trade_profit_brl
        self.trade_profit_usd = trade_profit_usd
        self.total_brl = total_brl
        self.total_usd = total_usd
        self.total_shares = total_shares

        # Create a TransactionHistory object, problemas com o transaction=xxx
        TransactionsHistory.objects.create(
            portfolio_investment=self.portfolio_investment,
            transaction=self.last_transaction,
            share_average_price_brl=self.share_average_price_brl,
            share_average_price_usd=self.share_average_price_usd,
            total_shares=self.total_shares,
            total_brl=self.total_brl,
            total_usd=self.total_usd,
            transaction_date=self.transaction_date
        )

        # Update the corresponding portfolio_investment
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

    def delete(self, *args, **kwargs):
        # Before deleting the object, we need to adjust the amount of shares in portfolio_investment
        if self.transaction_type == 'buy':
            self.portfolio_investment.shares_amount -= self.transaction_amount
            self.portfolio_investment.total_cost_brl -= self.transaction_amount * self.price_brl
            self.portfolio_investment.total_cost_usd -= self.transaction_amount * self.price_usd
        elif self.transaction_type == 'sell':
            self.portfolio_investment.shares_amount += self.transaction_amount
            sell_brl = self.transaction_amount * self.price_brl
            sell_usd = self.transaction_amount * self.price_usd
            cost_brl = self.transaction_amount * self.portfolio_investment.share_average_price_brl
            cost_usd = self.transaction_amount * self.portfolio_investment.share_average_price_usd
            self.portfolio_investment.trade_profit_brl -= sell_brl - cost_brl
            self.portfolio_investment.trade_profit_usd -= sell_usd - cost_usd
            self.portfolio_investment.total_cost_brl += cost_brl
            self.portfolio_investment.total_cost_usd += cost_usd
        self.portfolio_investment.save()

        # Then recalculate averages
        portfolio_average_price = AssetAveragePrice.objects.get(portfolio_investment=self.portfolio_investment)
        portfolio_average_price.recalculate_average(start_date=self.transaction_date, transaction_id=self.id)

        # Now we can delete the object
        super().delete(*args, **kwargs)

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

    class Meta:
        ordering = ['-transaction_date']
        verbose_name = 'Histórico de Transações'
        verbose_name_plural = 'Históricos de Transações'

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
    
    def save(self, *args, **kwargs):
        self.transaction.transaction_type = 'withdraw'
        self.transaction.save()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Despesa'
        verbose_name_plural = 'Despesas'

    def __str__(self):
        return f"{self.description} - {self.transaction.transaction_amount}"



