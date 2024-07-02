from django.db import models
from portfolios.models import Portfolio
from django.db import transaction
from django.db.models import Sum
from datetime import datetime
from cashflow.models import CurrencyTransaction, InternationalCurrencyTransfer
from timewarp.models import AssetHistoricalPrice, CurrencyHistoricalPrice
from trade.models import Trade
from brokers.models import Broker
from investments.models import Asset
from categories.models import Category

class QuotaHistory(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, default=11)
    event_type = models.CharField( 
        max_length=20,
        choices=[
            ('deposit', 'deposit'),
            ('withdraw', 'withdraw'),
            ('valuation', 'valuation'),
            ('dividend receive', 'dividend receive'),
            ('dividend payment', 'dividend payment'),
            ('invest br', 'invest br'),
            ('divest br', 'divest br'),
            ('invest us', 'invest us'),
            ('divest us', 'divest us'),
            ('tax payment', 'tax payment'),
            ('send money', 'send money'),
        ],
        default='deposit'
    )
    value_brl = models.FloatField(default=0)
    value_usd = models.FloatField(default=0) 
    date = models.DateTimeField(default=datetime.now)
    # Calculado Automaticamente
    total_brl = models.FloatField(default=0, editable=False)
    total_usd = models.FloatField(default=0, editable=False)
    quota_amount = models.FloatField(default=0, editable=False)
    quota_price_brl = models.FloatField(default=0, editable=False)
    quota_price_usd = models.FloatField(default=0, editable=False)
    percentage_change = models.FloatField(default=0, editable=False)

    def save(self, *args, **kwargs):
        portfolio_history = self.create_portfolio_history()
        self.create_quota_history(portfolio_history) 
        super().save(*args, **kwargs)

    def create_portfolio_history(self):
        portfolio_history = PortfolioTotalHistory.objects.create(
            portfolio=self.portfolio,
            date=self.date,
            event_type=self.event_type,
        )
        return portfolio_history

    def create_quota_history(self, portfolio_history):
        self.total_brl = portfolio_history.total_brl  
        self.total_usd = portfolio_history.total_usd  

        portfolio_quota_histories = QuotaHistory.objects.filter(portfolio=self.portfolio).order_by('-date')
        last_quota_history = portfolio_quota_histories.filter(date__lt=self.date).first()

        if last_quota_history:
            if self.event_type in ['deposit', 'withdraw']:
                self.quota_amount = last_quota_history.quota_amount + (self.value_brl / last_quota_history.quota_price_brl) if last_quota_history.quota_price_brl != 0 else 0
            else:
                self.quota_amount = last_quota_history.quota_amount

            self.quota_price_brl = self.total_brl / self.quota_amount if self.quota_amount != 0 else 0
            self.quota_price_usd = self.total_usd / self.quota_amount if self.quota_amount != 0 else 0
            self.percentage_change = (self.quota_price_brl / last_quota_history.quota_price_brl) - 1 if last_quota_history.quota_price_brl != 0 else 0

        else:
            if self.event_type == 'deposit':
                self.total_brl = self.value_brl
                self.total_usd = self.value_usd
                self.quota_amount = self.value_brl
                self.quota_price_brl = 1
                self.quota_price_usd = self.value_usd / self.value_brl if self.value_brl != 0 else 0
                self.percentage_change = 0
            else:
                raise Exception(f'Não há histórico de cotas para este portfolio, por isso voce não pode realizar a operação: {self.event_type}.')

    class Meta:
        verbose_name_plural = "Historico dos Portfolios - Cotas"
        ordering = ['-date']

class SubscriptionEvent(CurrencyTransaction):

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Make sure the transaction_type is always 'deposit'
        self.transaction_type = 'deposit' # deixar hidden no admin e frontend
        super().save(*args, **kwargs)

        value_brl = self.transaction_amount * self.price_brl
        value_usd = self.transaction_amount * self.price_usd
        
        QuotaHistory.objects.create(
            portfolio=self.portfolio,
            date=self.transaction_date,
            event_type='deposit',
            value_brl=value_brl,
            value_usd=value_usd,     
        )

    class Meta:
        verbose_name = 'Subscrição'
        verbose_name_plural = '     Subscrições - Aumento de Cotas'

class DividendReceiveEvent(CurrencyTransaction):

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Make sure the transaction_type is always 'deposit'
        self.transaction_type = 'deposit'
        super().save(*args, **kwargs)

        value_brl = self.transaction_amount * self.price_brl
        value_usd = self.transaction_amount * self.price_usd

        QuotaHistory.objects.create(
            portfolio=self.portfolio,
            date=self.transaction_date,
            event_type='dividend receive',
            value_brl=value_brl,
            value_usd=value_usd,
        )

    class Meta:
        verbose_name = 'Recebimento de Dividendos'
        verbose_name_plural = '  Recebimento de Dividendos'

class ValuationEvent(QuotaHistory):
    @transaction.atomic
    def save(self, *args, **kwargs):
        self.event_type = 'valuation'
        self.value_brl = 0  
        self.value_usd = 0 
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Valuation do Portfolio'
        verbose_name_plural = 'Valuation dos Portfolios'

class RedemptionEvent(CurrencyTransaction):
    @transaction.atomic
    def save(self, *args, **kwargs):
        self.transaction_type = 'withdraw'
        super().save(*args, **kwargs)

        value_brl = self.transaction_amount * self.price_brl * -1
        value_usd = self.transaction_amount * self.price_usd * -1

        QuotaHistory.objects.create(
            portfolio=self.portfolio,
            date=self.transaction_date,
            event_type='withdraw',
            value_brl=value_brl,
            value_usd=value_usd,     
        )
    
    class Meta:
        verbose_name = 'Resgate'
        verbose_name_plural = '   Resgates - Diminuição de Cotas'
  
class DividendPayEvent(CurrencyTransaction):
    @transaction.atomic
    def save(self, *args, **kwargs):
        # Make sure the transaction_type is always 'withdraw'
        self.transaction_type = 'withdraw'
        super().save(*args, **kwargs)

        value_brl = self.transaction_amount * self.price_brl * -1
        value_usd = self.transaction_amount * self.price_usd * -1

        QuotaHistory.objects.create(
            portfolio=self.portfolio,
            date=self.transaction_date,
            event_type='dividend payment',
            value_brl=value_brl,
            value_usd=value_usd,
        )
    
    class Meta:
        verbose_name = 'Pagamento de Dividendos'
        verbose_name_plural = ' Pagamento de Dividendos'

class TaxPayEvent(CurrencyTransaction):
    @transaction.atomic
    def save(self, *args, **kwargs):
        # Make sure the transaction_type is always 'withdraw'
        self.transaction_type = 'withdraw'
        super().save(*args, **kwargs)

        value_brl = self.transaction_amount * self.price_brl * -1
        value_usd = self.transaction_amount * self.price_usd * -1

        QuotaHistory.objects.create(
            portfolio=self.portfolio,
            date=self.transaction_date,
            event_type='tax payment',
            value_brl=value_brl,
            value_usd=value_usd,
        )
    
    class Meta:
        verbose_name = 'Pagamento de Impostos'
        verbose_name_plural = ' Pagamento de Impostos'

class InvestBrEvent(CurrencyTransaction):
    to_broker = models.ForeignKey(Broker, on_delete=models.CASCADE, default=1)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, default=1)
    trade_amount = models.FloatField(default=0)
    asset_price_brl = models.FloatField(default=0)

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.transaction_type = 'withdraw'
        trade = self.create_trade()
        self.transaction_amount = (trade.trade_amount * trade.price_brl) 
        super().save(*args, **kwargs)

        value_brl = self.transaction_amount * self.price_brl * -1
        value_usd = self.transaction_amount * self.price_usd * -1

        QuotaHistory.objects.create(
            portfolio=self.portfolio,
            date=self.transaction_date,
            event_type='invest br',
            value_brl=value_brl,
            value_usd=value_usd,
        )

    def create_trade(self):
        trade = Trade.objects.create(
            portfolio=self.portfolio,
            asset=self.asset,
            broker=self.to_broker,
            trade_amount=self.trade_amount,
            trade_date=self.transaction_date,
            trade_type='buy',
        )
        return trade

    class Meta:
        verbose_name_plural = '  Comprar / Investir no Brasil'

class DivestBrEvent(CurrencyTransaction):
    to_broker = models.ForeignKey(Broker, on_delete=models.CASCADE, default=1)  # Adicionado
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, default=1)
    trade_amount = models.FloatField(default=0)
    asset_price_brl = models.FloatField(default=0)

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Make sure the transaction_type is always 'deposit'
        self.transaction_type = 'deposit'
        self.transaction_amount = self.trade_amount * self.asset_price_brl  # Declaração explícita do preço do ativo
        trade = self.create_trade()
        self.transaction_amount = (trade.trade_amount * trade.price_brl) 
        super().save(*args, **kwargs)

        value_brl = self.transaction_amount * self.price_brl * -1
        value_usd = self.transaction_amount * self.price_usd * -1

        QuotaHistory.objects.create(
            portfolio=self.portfolio,
            date=self.transaction_date,
            event_type='divest br',
            value_brl=value_brl,
            value_usd=value_usd,
        )

    def create_trade(self):
        trade = Trade.objects.create(
            portfolio=self.portfolio,
            asset=self.asset,
            broker=self.to_broker,
            trade_amount=self.trade_amount,
            trade_date=self.transaction_date,
            trade_type='sell',
            price_brl=self.asset_price_brl,
        )
        return trade

    class Meta:
        verbose_name_plural = '  Vender / Desinvestir no Brasil'

class InvestUsEvent(CurrencyTransaction):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, default=1)
    trade_amount = models.FloatField(default=0)
    asset_price_usd = models.FloatField(default=0)

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Make sure the transaction_type is always 'withdraw'
        self.transaction_type = 'withdraw'
        trade = self.create_trade()
        self.transaction_amount = (trade.trade_amount * trade.price_usd) 
        super().save(*args, **kwargs)

        value_brl = self.transaction_amount * self.price_brl * -1
        value_usd = self.transaction_amount * self.price_usd * -1

        QuotaHistory.objects.create(
            portfolio=self.portfolio,
            date=self.transaction_date,
            event_type='invest us',
            value_brl=value_brl,
            value_usd=value_usd,
        )
    
    def create_trade(self):
        trade = Trade.objects.create(
            portfolio=self.portfolio,
            asset=self.asset,
            broker=self.broker,
            trade_amount=self.trade_amount,
            trade_date=self.transaction_date,
            trade_type='buy',
        )
        return trade

class DivestUsEvent(CurrencyTransaction):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, default=1)
    trade_amount = models.FloatField(default=0)
    asset_price_usd = models.FloatField(default=0)

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Make sure the transaction_type is always 'deposit'
        self.transaction_type = 'deposit'
        trade = self.create_trade()
        self.transaction_amount = (trade.trade_amount * trade.price_usd) 
        super().save(*args, **kwargs)

        value_brl = self.transaction_amount * self.price_brl * -1
        value_usd = self.transaction_amount * self.price_usd * -1

        QuotaHistory.objects.create(
            portfolio=self.portfolio,
            date=self.transaction_date,
            event_type='divest us',
            value_brl=value_brl,
            value_usd=value_usd,
        )

    def create_trade(self):
        trade = Trade.objects.create(
            portfolio=self.portfolio,
            asset=self.asset,
            broker=self.broker,
            trade_amount=self.trade_amount,
            trade_date=self.transaction_date,
            trade_type='sell',
            price_usd=self.asset_price_usd,
        )
        return trade

class PortfolioHistoryByCategory(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateField()
    total_brl = models.FloatField()
    total_usd = models.FloatField()

    def __str__(self):
        return f'{self.portfolio.name} - {self.category.name} - {self.date}'

    class Meta:
        verbose_name_plural = 'Histórico de Portfólios por Categoria'
        ordering = ('-date', 'category',)

class PortfolioTotalHistory(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    date = models.DateField()
    total_brl = models.FloatField()
    total_usd = models.FloatField()
    event_type = models.CharField(max_length=20, default='none')


    def __str__(self):
        return f'{self.portfolio.name} - {self.date}'

    class Meta:
        verbose_name_plural = 'Histórico de Portfolios'

    def get_transactions_totals(self, investment):
        buy_trades = Trade.objects.filter(
            portfolio_investment=investment,
            trade_type='buy',
            trade_date__lte=self.date
        ).aggregate(Sum('trade_amount'))['trade_amount__sum'] or 0

        sell_trades = Trade.objects.filter(
            portfolio_investment=investment,
            trade_type='sell',
            trade_date__lte=self.date
        ).aggregate(Sum('trade_amount'))['trade_amount__sum'] or 0

        deposits = CurrencyTransaction.objects.filter(
            portfolio_investment=investment,
            transaction_type='deposit',
            transaction_date__lte=self.date
        ).aggregate(Sum('transaction_amount'))['transaction_amount__sum'] or 0

        withdraws = CurrencyTransaction.objects.filter(
            portfolio_investment=investment,
            transaction_type='withdraw',
            transaction_date__lte=self.date
        ).aggregate(Sum('transaction_amount'))['transaction_amount__sum'] or 0

        return buy_trades, sell_trades, deposits, withdraws

    def get_historical_price_and_exchange_rate(self, investment, currency_pair):
        try:
            historical_price = AssetHistoricalPrice.objects.filter(
                asset=investment.asset,
                date__lte=self.date,
            ).latest('date')
        except AssetHistoricalPrice.DoesNotExist:
            historical_price = None

        try:
            exchange_rate = CurrencyHistoricalPrice.objects.filter(
                currency_pair=currency_pair, 
                date__lte=self.date  
            ).latest('date')
        except CurrencyHistoricalPrice.DoesNotExist:
            exchange_rate = None

        return historical_price, exchange_rate

    def calculate_total_values(self, investment, historical_price, exchange_rate):
        total_brl = 0
        total_usd = 0

        # verificar aqui se é / ou * no cálculo do total_usd e vice-versa
        if historical_price:
            if investment.broker.main_currency.ticker == 'BRL':
                total_brl += historical_price.close * investment.shares_amount
                if exchange_rate:
                    total_usd += (historical_price.close * investment.shares_amount) * exchange_rate.close
            elif investment.broker.main_currency.ticker == 'USD':
                total_usd += historical_price.close * investment.shares_amount
                if exchange_rate:
                    total_brl += (historical_price.close * investment.shares_amount) * exchange_rate.close
        return total_brl, total_usd

    def calculate_totals_by_category(self, portfolio_investments):
        category_totals = {}

        for investment in portfolio_investments:
            buy_trades, sell_trades, deposits, withdraws = self.get_transactions_totals(investment)

            if buy_trades - sell_trades + deposits - withdraws > 0:
                currency_pair = 'BRLUSD' if investment.broker.main_currency.ticker == 'BRL' else 'USDBRL'
                historical_price, exchange_rate = self.get_historical_price_and_exchange_rate(investment, currency_pair)

                total_brl_investment, total_usd_investment = self.calculate_total_values(investment, historical_price, exchange_rate)

                category = investment.asset.category
                if category not in category_totals:
                    category_totals[category] = {'total_brl': 0, 'total_usd': 0}
                category_totals[category]['total_brl'] += total_brl_investment
                category_totals[category]['total_usd'] += total_usd_investment

        return category_totals

    def save(self, *args, **kwargs):
        portfolio_investments = self.portfolio.portfolioinvestment_set.all()

        total_brl = 0
        total_usd = 0

        category_totals = self.calculate_totals_by_category(portfolio_investments)

        for totals in category_totals.values():
            total_brl += totals['total_brl']
            total_usd += totals['total_usd']

        self.total_brl = total_brl
        self.total_usd = total_usd

        super().save(*args, **kwargs)

        # Salvando os totais por categoria apenas no valuation
        if self.event_type == 'valuation':
            for category, totals in category_totals.items():
                PortfolioHistoryByCategory.objects.create(
                    portfolio=self.portfolio,
                    category=category,
                    date=self.date,
                    total_brl=totals['total_brl'],
                    total_usd=totals['total_usd']
                )

    class Meta:
        verbose_name_plural = 'Histórico dos Portfolios - Total'

class SendMoneyEvent(InternationalCurrencyTransfer):
     
    @transaction.atomic
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        QuotaHistory.objects.create(
            portfolio=self.portfolio,
            date=self.transfer_date,
            event_type='send money',
            value_brl=0,
            value_usd=0,
        )

    class Meta:
        verbose_name = 'Envio de Dinheiro'
        verbose_name_plural = '  Envio de Dinheiro'