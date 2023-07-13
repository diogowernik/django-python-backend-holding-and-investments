from django.db import models
from brokers.models import Broker
from portfolios.models import Portfolio, PortfolioInvestment
from investments.models import Asset
from django.utils import timezone
from django.db import transaction # @transaction.atomic
from django.apps import apps
from trade.services.price_services import set_prices
from trade.services.currency_transaction_service import create_or_update_currency_transaction, delete_currency_transaction
from trade.services.portfolio_investment_service import set_portfolio_investment, adjust_portfolio_investment, update_portfolio_investment
from trade.services.dividends_service import update_portfolio_dividend, update_portfolio_dividend_fields, create_portfolio_dividend

# Compra e venda de ativos (Reit, BrStocks, Fii, Stocks)
class Trade(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, default=11)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, default=1)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, default=1)
    transaction_type = models.CharField(max_length=50, choices=(('buy', 'Buy'), ('sell', 'Sell')), default='buy')
    transaction_amount = models.FloatField(default=0)
    transaction_date = models.DateTimeField(default=timezone.now)
    price_brl = models.FloatField(null=True, blank=True)
    price_usd = models.FloatField(null=True, blank=True)
    portfolio_investment = models.ForeignKey(PortfolioInvestment, on_delete=models.CASCADE, blank=True, null=True)

    # Save the object and call needed methods
    @transaction.atomic
    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if the object is new
        set_prices(self)
        set_portfolio_investment(self)
        super().save(*args, **kwargs)  # Save the object
        create_or_update_currency_transaction(self)
        self.process_transaction(is_new)

    # Send data to TradeCalculation
    def process_transaction(self, is_new):
        transaction_calculation, _ = TradeCalculation.objects.get_or_create(portfolio_investment=self.portfolio_investment)
        transaction_calculation.transaction_date = self.transaction_date
        transaction_calculation.last_transaction = self
        transaction_calculation.process_transaction(transaction_date=self.transaction_date, is_new=is_new)
        transaction_calculation.save()

    @transaction.atomic  
    def delete(self, *args, **kwargs):
        adjust_portfolio_investment(self)
        self.reprocess_trade()
        delete_currency_transaction(self)
        self.delete_trade_history()

        super().delete(*args, **kwargs)

    def delete_trade_history(self):
        # Aqui vamos pegar a TradeHistory associada a essa Trade e chamar o método delete.
        try:
            trade_history = TradeHistory.objects.get(transaction=self)
            trade_history.delete()
        except TradeHistory.DoesNotExist:
            pass

    # Reprocess the transaction when the asset transaction is deleted
    def reprocess_trade(self):
        try:
            transaction_calculation = TradeCalculation.objects.get(portfolio_investment=self.portfolio_investment)
            transaction_calculation.process_transaction(transaction_date=self.transaction_date, transaction_id=self.id)
        except TradeCalculation.DoesNotExist:
            pass

    class Meta:
        ordering = ['-transaction_date']
        verbose_name = ' Compra e Venda de Ativo'
        verbose_name_plural = ' Compra e Venda de Ativos'

    def __str__(self):
        return f'{self.asset.ticker} - {self.transaction_date.strftime("%d/%m/%Y")}'

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
    transaction_date = models.DateTimeField(default=timezone.now)

    def process_transaction(self, transaction_date, is_new=False, transaction_id=None): 
        transactions = self.get_transactions(transaction_id)
        total_brl, total_usd, total_shares, trade_profit_brl, trade_profit_usd, share_avg_price_brl, share_avg_price_usd = self.calculate_totals_and_profits(transactions)
        transactions_until_date = self.get_transactions_until_date(transaction_date)
        total_brl_until_date, total_usd_until_date, total_shares_until_date, _, _, _, _ = self.calculate_totals_and_profits(transactions_until_date)
        self.update_self_values(total_brl, total_usd, total_shares, trade_profit_brl, trade_profit_usd)
        self.create_or_update_trade_history(total_brl_until_date, total_usd_until_date, total_shares_until_date, share_avg_price_brl, share_avg_price_usd)
        update_portfolio_investment(self, total_brl, total_usd, total_shares)

        # Se a transação for uma atualização, reprocessar as TradeHistory seguintes.
        if not is_new:
            self.reprocess_following_transaction_histories(self.last_transaction)

    def get_transactions(self, transaction_id):
        return Trade.objects.filter(portfolio_investment=self.portfolio_investment).exclude(id=transaction_id).order_by('transaction_date')

    def get_transactions_until_date(self, transaction_date):
        return Trade.objects.filter(portfolio_investment=self.portfolio_investment, transaction_date__lte=transaction_date).order_by('transaction_date')

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

    def create_or_update_trade_history(self, total_brl_until_date, total_usd_until_date, total_shares_until_date, share_avg_price_brl_until_date, share_avg_price_usd_until_date):
        # Verifique se já existe um histórico de transações para esta transação
        trade_history, created = TradeHistory.objects.get_or_create(
            portfolio_investment=self.portfolio_investment,
            transaction=self.last_transaction,
            defaults={
                'share_average_price_brl': share_avg_price_brl_until_date,
                'share_average_price_usd': share_avg_price_usd_until_date,
                'total_shares': total_shares_until_date,
                'total_brl': total_brl_until_date,
                'total_usd': total_usd_until_date,
                'transaction_date': self.transaction_date
            }
        )

        # Se a instância do TradeHistory já existia, atualize seus campos
        if not created:
            trade_history.share_average_price_brl = share_avg_price_brl_until_date
            trade_history.share_average_price_usd = share_avg_price_usd_until_date
            trade_history.total_shares = total_shares_until_date
            trade_history.total_brl = total_brl_until_date
            trade_history.total_usd = total_usd_until_date
            trade_history.transaction_date = self.transaction_date
            trade_history.save()

    def reprocess_following_transaction_histories(self, asset_transaction):
        # Obter todas as TradeHistory após a data da asset_transaction
        following_transaction_histories = TradeHistory.objects.filter(
            transaction__transaction_date__gt=asset_transaction.transaction_date,
            transaction__asset=asset_transaction.asset
        ).order_by('transaction__transaction_date')

        # Se não houver TradeHistory após a data, sair da função
        if not following_transaction_histories.exists():
            return

        # Redefinir a contagem total de ações
        total_shares = asset_transaction.transaction_amount

        # Iterar através de cada TradeHistory e atualizar o total_shares
        for trade_history in following_transaction_histories:
            if trade_history.transaction.transaction_type == 'buy':
                total_shares += trade_history.transaction.transaction_amount
            elif trade_history.transaction.transaction_type == 'sell':
                total_shares -= trade_history.transaction.transaction_amount

            # Atualizar o total_shares de trade_history
            trade_history.total_shares = total_shares
            trade_history.save()

    class Meta:
        ordering = ['-transaction_date']
        verbose_name = ' Compra e Venda / Calculos'
        verbose_name_plural = ' Compras e Vendas / Calculos'

# Histórico de Preço Médio do Ativo, Total de Ações, Total em BRL e Total em USD, Transação
class TradeHistory(models.Model):
    portfolio_investment = models.ForeignKey(PortfolioInvestment, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Trade, on_delete=models.DO_NOTHING)
    share_average_price_brl = models.FloatField()
    share_average_price_usd = models.FloatField()
    total_shares = models.FloatField()
    total_brl = models.FloatField()
    total_usd = models.FloatField()
    transaction_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            create_portfolio_dividend(self)
        else:
            update_portfolio_dividend(self)
                
    def get_transaction_data(self, record_date):
        transaction_histories_before_record_date = self.__class__.objects.filter(
            portfolio_investment=self.portfolio_investment,
            transaction_date__lt=record_date
        ).order_by('-transaction_date')  # Ordenar do mais recente para o mais antigo

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
        transaction_date = self.transaction_date
        super().delete(*args, **kwargs)
        self.reprocess_portfolios_dividends(portfolio_investment, transaction_date)
    
    def reprocess_portfolios_dividends(self, portfolio_investment, transaction_date):
        PortfolioDividend = apps.get_model('dividends', 'PortfolioDividend')

        portfolio_dividends = PortfolioDividend.objects.filter(portfolio_investment=portfolio_investment)

        for portfolio_dividend in portfolio_dividends:
            # Aqui estamos obtendo os dados da transação considerando a data de registro do dividendo
            transaction_data = self.get_transaction_data(portfolio_dividend.record_date)

            # Encontrando a última transação antes da transação que estamos excluindo
            last_transaction = self.__class__.objects.filter(
                portfolio_investment=portfolio_investment, 
                transaction_date__lt=transaction_date
            ).order_by('-transaction_date').first()

            if last_transaction:
                portfolio_dividend.trade_history = last_transaction
                update_portfolio_dividend_fields(self, portfolio_dividend, transaction_data)
            else:
                # Se não houver transação anterior, a portfolio_dividend deve ser excluída
                portfolio_dividend.delete()

    class Meta:
        ordering = ['-transaction_date']
        verbose_name = ' Compra e Venda / Histórico'
        verbose_name_plural = ' Compras e Vendas / Histórico'
