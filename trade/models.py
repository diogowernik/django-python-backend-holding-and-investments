from django.db import models
from brokers.models import Broker
from portfolios.models import Portfolio, PortfolioInvestment
from investments.models import Asset
from django.utils import timezone
from django.db import transaction # @transaction.atomic
from trade.services.price_services import set_prices
from trade.services.currency_transaction_service import create_or_update_currency_transaction, delete_currency_transaction
from trade.services.portfolio_investment_service import set_portfolio_investment, adjust_portfolio_investment, update_portfolio_investment
from trade.services.dividends_service import update_portfolio_dividend, update_portfolio_dividend_fields, create_portfolio_dividend

# Serviços    
class HistoryService:
    def create_or_update_trade_history(self, trade_calculation, total_brl_until_date, total_usd_until_date, total_shares_until_date, share_avg_price_brl_until_date, share_avg_price_usd_until_date):
        trade_history, created = TradeHistory.objects.get_or_create(
            portfolio_investment=trade_calculation.portfolio_investment,
            transaction=trade_calculation.last_transaction,
            defaults={
                'share_average_price_brl': share_avg_price_brl_until_date,
                'share_average_price_usd': share_avg_price_usd_until_date,
                'total_shares': total_shares_until_date,
                'total_brl': total_brl_until_date,
                'total_usd': total_usd_until_date,
                'trade_date': trade_calculation.trade_date
            }
        )
        if not created:
            trade_history.share_average_price_brl = share_avg_price_brl_until_date
            trade_history.share_average_price_usd = share_avg_price_usd_until_date
            trade_history.total_shares = total_shares_until_date
            trade_history.total_brl = total_brl_until_date
            trade_history.total_usd = total_usd_until_date
            trade_history.trade_date = trade_calculation.trade_date
            trade_history.save()     

    def reprocess_following_transaction_histories(self, asset_transaction):
        following_transaction_histories = TradeHistory.objects.filter(
            transaction__trade_date__gt=asset_transaction.trade_date,
            transaction__asset=asset_transaction.asset
        ).order_by('transaction__trade_date')

        if not following_transaction_histories.exists():
            return

        total_shares = asset_transaction.trade_amount

        for trade_history in following_transaction_histories:
            if trade_history.transaction.trade_type == 'buy':
                total_shares += trade_history.transaction.trade_amount
            elif trade_history.transaction.trade_type == 'sell':
                total_shares -= trade_history.transaction.trade_amount

            trade_history.total_shares = total_shares
            trade_history.save()

    def delete_trade_history(self, trade): 
        try:
            trade_history = TradeHistory.objects.get(transaction=trade)
            trade_history.delete()
        except TradeHistory.DoesNotExist:
            pass
history_service = HistoryService()

class CalculationService: 
    def process_trade(self, trade, is_new):
        transaction_calculation, _ = TradeCalculation.objects.get_or_create(portfolio_investment=trade.portfolio_investment)
        transaction_calculation.trade_date = trade.trade_date
        transaction_calculation.last_transaction = trade
        transaction_calculation.process_transaction(trade_date=trade.trade_date, is_new=is_new)
        transaction_calculation.save()

    def reprocess_trade(self, trade):
        try:
            transaction_calculation = TradeCalculation.objects.get(portfolio_investment=trade.portfolio_investment)
            transaction_calculation.process_transaction(trade_date=trade.trade_date, transaction_id=trade.id)
        except TradeCalculation.DoesNotExist:
            pass
calculation_service = CalculationService()

# Compra e venda de ativos (Reit, BrStocks, Fii, Stocks)
class Trade(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, default=11)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, default=1)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, default=1)
    trade_type = models.CharField(max_length=50, choices=(('buy', 'Buy'), ('sell', 'Sell')), default='buy')
    trade_amount = models.FloatField(default=0)
    trade_date = models.DateTimeField(default=timezone.now)
    price_brl = models.FloatField(null=True, blank=True)
    price_usd = models.FloatField(null=True, blank=True)
    portfolio_investment = models.ForeignKey(PortfolioInvestment, on_delete=models.CASCADE, blank=True, null=True)

    # Save the object and call needed methods
    @transaction.atomic
    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if the object is new
        # services/price_services.py
        set_prices(self)
        # services/portfolio_investment_service.py
        set_portfolio_investment(self)
        super().save(*args, **kwargs)  # Save the object
        # CalculationService
        calculation_service.process_trade(self, is_new)

    @transaction.atomic  
    def delete(self, *args, **kwargs):
        # services/portfolio_investment_service.py
        adjust_portfolio_investment(self)
        # CalculationService
        calculation_service.reprocess_trade(self)
        # services/history_service.py
        history_service.delete_trade_history(self)

        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['-trade_date']
        verbose_name = ' Compra e Venda de Ativo'
        verbose_name_plural = ' Compra e Venda de Ativos'

    def __str__(self):
        return f'{self.asset.ticker} - {self.trade_date.strftime("%d/%m/%Y")}'

class TradeService:
    def get_transactions(self, portfolio_investment, transaction_id=None):
        return Trade.objects.filter(portfolio_investment=portfolio_investment).exclude(id=transaction_id).order_by('trade_date')

    def get_transactions_until_date(self, portfolio_investment, trade_date):
        return Trade.objects.filter(portfolio_investment=portfolio_investment, trade_date__lte=trade_date).order_by('trade_date')
trade_service = TradeService()

class TradeCalculation(models.Model):
    portfolio_investment = models.OneToOneField(PortfolioInvestment, on_delete=models.CASCADE)
    last_transaction = models.ForeignKey(Trade, null=True, blank=True, on_delete=models.SET_NULL) # SET_NULL importante, não queremos deletar o objeto pois ele representa um estado.
    share_average_price_brl = models.FloatField(default=0)
    share_average_price_usd = models.FloatField(default=0)
    trade_profit_brl = models.FloatField(default=0)
    trade_profit_usd = models.FloatField(default=0)
    total_shares = models.FloatField(default=0)
    total_brl = models.FloatField(default=0)
    total_usd = models.FloatField(default=0)
    trade_date = models.DateTimeField(default=timezone.now)

    def process_transaction(self, trade_date, is_new=False, transaction_id=None): 
        # TradeService
        transactions = trade_service.get_transactions(self.portfolio_investment, transaction_id)
        transactions_until_date = trade_service.get_transactions_until_date(self.portfolio_investment, trade_date)

        # self
        total_brl, total_usd, total_shares, trade_profit_brl, trade_profit_usd, share_avg_price_brl, share_avg_price_usd = self.calculate_totals_and_profits(transactions)
        total_brl_until_date, total_usd_until_date, total_shares_until_date, _, _, _, _ = self.calculate_totals_and_profits(transactions_until_date)
        self.update_self_values(total_brl, total_usd, total_shares, trade_profit_brl, trade_profit_usd)
        
        # services/portfolio_investment_service.py
        update_portfolio_investment(self, total_brl, total_usd, total_shares)

        # HistoryService
        history_service.create_or_update_trade_history(self, total_brl_until_date, total_usd_until_date, total_shares_until_date, 
        share_avg_price_brl, share_avg_price_usd)
        # Se a transação for uma atualização, reprocessar as TradeHistory seguintes.
        if not is_new:
            history_service.reprocess_following_transaction_histories(self.last_transaction)

    def calculate_totals_and_profits(self, transactions):
        total_brl = 0
        total_usd = 0
        total_shares = 0
        trade_profit_brl = 0
        trade_profit_usd = 0
        for transaction in transactions:
            if transaction.trade_type == 'buy':
                total_brl += transaction.trade_amount * transaction.price_brl
                total_usd += transaction.trade_amount * transaction.price_usd
                total_shares += transaction.trade_amount
            elif transaction.trade_type == 'sell':
                sell_brl = transaction.trade_amount * transaction.price_brl
                sell_usd = transaction.trade_amount * transaction.price_usd
                cost_brl = transaction.trade_amount * self.share_average_price_brl
                cost_usd = transaction.trade_amount * self.share_average_price_usd
                
                trade_profit_brl += sell_brl - cost_brl
                trade_profit_usd += sell_usd - cost_usd
                
                total_brl -= cost_brl
                total_usd -= cost_usd
                total_shares -= transaction.trade_amount

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

    class Meta:
        ordering = ['-trade_date']
        verbose_name = ' Compra e Venda / Calculos'
        verbose_name_plural = ' Compras e Vendas / Calculos'

class DividendService:
    def reprocess_portfolios_dividends(self, trade_history, portfolio_investment, trade_date):
        from django.apps import apps
        PortfolioDividend = apps.get_model('dividends', 'PortfolioDividend')

        portfolio_dividends = PortfolioDividend.objects.filter(portfolio_investment=portfolio_investment)

        for portfolio_dividend in portfolio_dividends:
            # Aqui estamos obtendo os dados da transação considerando a data de registro do dividendo
            transaction_data = trade_history.get_transaction_data(portfolio_dividend.record_date)

            # Encontrando a última transação antes da transação que estamos excluindo
            last_transaction = TradeHistory.objects.filter(
                portfolio_investment=portfolio_investment, 
                trade_date__lt=trade_date
            ).order_by('-trade_date').first()

            if last_transaction:
                portfolio_dividend.trade_history = last_transaction
                update_portfolio_dividend_fields(self, portfolio_dividend, transaction_data)
            else:
                # Se não houver transação anterior, a portfolio_dividend deve ser excluída
                portfolio_dividend.delete()
dividend_service = DividendService()

# Histórico de Preço Médio do Ativo, Total de Ações, Total em BRL e Total em USD, Transação
class TradeHistory(models.Model):
    portfolio_investment = models.ForeignKey(PortfolioInvestment, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Trade, on_delete=models.DO_NOTHING)
    share_average_price_brl = models.FloatField()
    share_average_price_usd = models.FloatField()
    total_shares = models.FloatField()
    total_brl = models.FloatField()
    total_usd = models.FloatField()
    trade_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # services/dividend_service.py
            create_portfolio_dividend(self)
        else:
            # services/dividend_service.py
            update_portfolio_dividend(self)

    # self    
    def get_transaction_data(self, record_date):
        transaction_histories_before_record_date = self.__class__.objects.filter(
            portfolio_investment=self.portfolio_investment,
            trade_date__lt=record_date
        ).order_by('-trade_date')  # Ordenar do mais recente para o mais antigo

        last_trade_history_before_record_date = transaction_histories_before_record_date.first()

        if last_trade_history_before_record_date:
            total_shares = last_trade_history_before_record_date.total_shares
            average_price_brl = last_trade_history_before_record_date.share_average_price_brl
            average_price_usd = last_trade_history_before_record_date.share_average_price_usd
        else:
            total_shares = 0
            average_price_brl = 0
            average_price_usd = 0
        return total_shares, average_price_brl, average_price_usd

    def delete(self, *args, **kwargs):
        portfolio_investment = self.portfolio_investment
        trade_date = self.trade_date
        super().delete(*args, **kwargs)

        # services/dividend_service.py
        dividend_service.reprocess_portfolios_dividends(self, portfolio_investment, trade_date)


    class Meta:
        ordering = ['-trade_date']
        verbose_name = ' Compra e Venda / Histórico'
        verbose_name_plural = ' Compras e Vendas / Histórico'
