from django.db import models
from investments.models import Asset
from portfolios.models import PortfolioInvestment, Portfolio
from trade.models import TradeHistory
from categories.models import Category
from django.db.models import Max
from timewarp.models import CurrencyHistoricalPrice
from equity.models import DividendReceiveEvent

class Dividend(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="dividends", default=1)
    value_per_share_brl = models.FloatField(default=0)
    value_per_share_usd = models.FloatField(default=0) # criar uma conversão automática na data.
    record_date = models.DateTimeField(null=True, blank=True)
    pay_date = models.DateTimeField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='BRL')

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super(Dividend, self).save(*args, **kwargs)  # salvando o Dividendo primeiro
        if is_new:
            self.create_portfolio_dividends()
        else:
            self.update_portfolio_dividends()
    
    def update_portfolio_dividends(self):
        portfolio_dividends = PortfolioDividend.objects.filter(dividend=self)
        for portfolio_dividend in portfolio_dividends:
            portfolio_dividend.value_per_share_brl = self.value_per_share_brl
            portfolio_dividend.value_per_share_usd = self.value_per_share_usd
            portfolio_dividend.save()

    def create_portfolio_dividends(self):
        portfolio_investment_objs = self.get_portfolio_investments()
        latest_transactions_dict = self.get_latest_transactions(portfolio_investment_objs)

        for portfolio_investment_obj in portfolio_investment_objs:
            last_trade_date = latest_transactions_dict.get(portfolio_investment_obj.id)
            if last_trade_date is not None:
                latest_asset_transaction = TradeHistory.objects.filter(
                    portfolio_investment=portfolio_investment_obj,
                    trade_date=last_trade_date
                ).first()
                self.create_dividends_for_portfolios(latest_asset_transaction)

    def get_portfolio_investments(self):
        portfolio_investments_by_asset = PortfolioInvestment.objects.filter(
            asset=self.asset
        ).values('broker', 'portfolio').distinct()

        return PortfolioInvestment.objects.filter(
            broker__in=[x['broker'] for x in portfolio_investments_by_asset],
            portfolio__in=[x['portfolio'] for x in portfolio_investments_by_asset],
            asset=self.asset
        )

    def get_latest_transactions(self, portfolio_investment_objs):
        latest_transactions = TradeHistory.objects.filter(
            portfolio_investment__in=portfolio_investment_objs,
            trade_date__lte=self.record_date
        ).values('portfolio_investment').annotate(
            last_trade_date=Max('trade_date')
        )
        return {x['portfolio_investment']: x['last_trade_date'] for x in latest_transactions}
    
    def get_latest_asset_transaction(self, portfolio_investment_obj):
        historical_average_prices = TradeHistory.objects.filter(portfolio_investment=portfolio_investment_obj, trade_date__lte=self.record_date)
        
        if historical_average_prices.exists():
            return historical_average_prices.latest('trade_date')
        return None

    def create_dividends_for_portfolios(self, latest_asset_transaction):
        if latest_asset_transaction.total_shares > 0:
            # Crie PortfolioDividend através da função centralizada
            # portfolio_dividend = PortfolioDividend.create_portfolio_dividend(latest_asset_transaction, self)
            PortfolioDividend.create_portfolio_dividend(latest_asset_transaction, self)
        
    def delete(self, *args, **kwargs):
        portfolio_dividends = PortfolioDividend.objects.filter(dividend=self)
        portfolio_dividends.delete()
        super(Dividend, self).delete(*args, **kwargs)

    def __str__(self):
        return '  {}  |  {}  |  {}  |  {}  '.format(self.asset.ticker, self.value_per_share_brl, self.record_date, self.pay_date)

    class Meta:
        verbose_name_plural = "Dividendos"

class PortfolioDividend(models.Model):
    portfolio_investment = models.ForeignKey(PortfolioInvestment, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    trade_history = models.ForeignKey(TradeHistory, on_delete=models.CASCADE, null=True, blank=True)
    dividend = models.ForeignKey(Dividend, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    record_date = models.DateTimeField(null=True, blank=True)
    pay_date = models.DateTimeField(null=True, blank=True)
    shares_amount = models.FloatField(default=0)
    value_per_share_brl = models.FloatField(default=0)
    value_per_share_usd = models.FloatField(default=0)
    average_price_brl = models.FloatField(default=0)
    average_price_usd = models.FloatField(default=0)
    currency = models.CharField(max_length=3, default='BRL')
    total_dividend_brl = models.FloatField(default=0, null=True, blank=True, editable=False)
    total_dividend_usd = models.FloatField(default=0, null=True, blank=True, editable=False)

    @classmethod
    def create_portfolio_dividend(cls, trade_history, dividend):
        portfolio_dividend = cls.objects.create(
            portfolio_investment=trade_history.portfolio_investment,
            asset=dividend.asset,
            trade_history=trade_history,
            category=dividend.asset.category,
            record_date=dividend.record_date,
            pay_date=dividend.pay_date,
            value_per_share_brl=dividend.value_per_share_brl,
            value_per_share_usd=dividend.value_per_share_usd,
            dividend=dividend,
            shares_amount=trade_history.total_shares, 
            average_price_brl=trade_history.share_average_price_brl,
            average_price_usd=trade_history.share_average_price_usd,
            currency=dividend.currency  # Definindo a currency com base no objeto dividend
        )
        return portfolio_dividend

    def save(self, *args, **kwargs):
        self.category = self.asset.category
        # arredondar para 4 casas decimais
        self.value_per_share_brl = round(self.value_per_share_brl, 4)
        self.value_per_share_usd = round(self.value_per_share_usd, 4)
        # calcular o total do dividendo
        self.total_dividend_brl = round(self.shares_amount * self.value_per_share_brl, 2)
        self.total_dividend_usd = round(self.shares_amount * self.value_per_share_usd, 2)
        super().save(*args, **kwargs)
    #     self.create_dividend_receive_events()  # Cria o DividendReceiveEvent automaticamente

    # def create_dividend_receive_events(self):
    #     if self.currency == 'BRL':
    #         transaction_amount = self.shares_amount * self.value_per_share_brl
    #     else:
    #         transaction_amount = self.shares_amount * self.value_per_share_usd

    #     DividendReceiveEvent.objects.create(
    #         portfolio = self.portfolio_investment.portfolio,
    #         broker = self.portfolio_investment.broker,
    #         transaction_amount = transaction_amount,
    #         transaction_date = self.pay_date,
    #         description = f'Dividendos recebido de {self.asset.ticker}, {transaction_amount} {self.currency}',
    #     )

    @property
    def pay_date_by_month_year(self):
        return self.pay_date.strftime('%m/%Y')

    @property
    def pay_date_by_year(self):
        return self.pay_date.strftime('%Y')

class DividendBr(Dividend):
    def save(self, *args, **kwargs):
        # Obtém o preço de fechamento do par BRLUSD mais recente antes da data de pagamento do dividendo
        try:
            currency_price = CurrencyHistoricalPrice.objects.filter(
                currency_pair="BRLUSD",
                date__lte=self.pay_date
            ).latest('date')
        except CurrencyHistoricalPrice.DoesNotExist:
            # Error message
            print("Não foi possível encontrar o preço de fechamento do par BRLUSD adicione o preço manualmente.")
            return

        # Converte o valor do dividendo de BRL para USD usando o preço de fechamento
        self.value_per_share_usd = self.value_per_share_brl * currency_price.close
        self.currency = 'BRL'

        super().save(*args, **kwargs)


    def __str__(self):
        return '  {}  |  {}  |  {}  |  {}  '.format(self.asset.ticker, self.value_per_share_brl, self.record_date, self.pay_date)

    class Meta:
        verbose_name_plural = "Dividendos BR"

class DividendUs(Dividend):
    def save(self, *args, **kwargs):
        # Obtém o preço de fechamento do par USDBRL mais recente antes da data de pagamento do dividendo
        try:
            currency_price = CurrencyHistoricalPrice.objects.filter(
                currency_pair="USDBRL",
                date__lte=self.pay_date.date()
            ).latest('date')
        except CurrencyHistoricalPrice.DoesNotExist:
            # Error message
            print("Não foi possível encontrar o preço de fechamento do par BRLUSD adicione o preço manualmente.")
            return

        # Converte o valor do dividendo de USD para BRL usando o preço de fechamento
        self.value_per_share_brl = self.value_per_share_usd * currency_price.close
        self.currency = 'USD'

        super().save(*args, **kwargs)

    def __str__(self):
        return '  {}  |  {}  |  {}  |  {}  '.format(self.asset.ticker, self.value_per_share_usd, self.record_date, self.pay_date)

    class Meta:
        verbose_name_plural = "Dividendos US"

class AccumulatedDividends(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField()
    accumulated_dividends_brl = models.FloatField(default=0)
    accumulated_dividends_usd = models.FloatField(default=0)

    class Meta:
        verbose_name = "Dividendo Acumulado"
        verbose_name_plural = "Dividendos Acumulados"
        unique_together = ('portfolio', 'year', 'month')
    @property
    def pay_date_by_month_year(self):
        return self.pay_date.strftime('%m/%Y')

    @property
    def pay_date_by_year(self):
        return self.pay_date.strftime('%Y')

    @property
    def yield_on_cost_brl(self):
        if self.average_price_brl > 0:
            return round((self.value_per_share_brl / self.average_price_brl), 4)

    @property
    def yield_on_cost_usd(self):
        if self.average_price_usd > 0:
            return round((self.value_per_share_usd / self.average_price_usd), 4)
        
    def __str__(self):
        return '  {}  |  {}  |  {}  |  {}  '.format(self.asset.ticker, self.value_per_share_brl, self.record_date, self.pay_date)
    
    class Meta:
        verbose_name_plural = "Dividendos por Portfolio"