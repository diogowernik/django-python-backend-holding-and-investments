from django.db import models
from investments.models import Asset
from portfolios.models import Portfolio, PortfolioInvestment

class Expiration(models.Model):
    """Model representing an option expiration date."""
    date = models.DateField(unique=True)

    def __str__(self):
        return f"Expiration Date: {self.date}"

class Option(models.Model):
    """Model representing a general option."""
    option_ticker = models.CharField(max_length=20) # Ticker
    option_type = models.CharField(max_length=4, choices=[
        ('CALL', 'Call'),
        ('PUT', 'Put')
    ], default='CALL') # Tipo
    has_market_maker = models.BooleanField(default=False) # F.M.
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE) # Asset.ticker eu informo o ticker do ativo
    expiration = models.ForeignKey(Expiration, on_delete=models.CASCADE) # Expiration.date eu informo a data de vencimento
    price_brl = models.FloatField() # Último
    strike_price = models.FloatField() # Strike

    def __str__(self):
        return f"{self.asset.ticker} - {self.option_type} - Expires on {self.expiration.date}"

    def save(self, *args, **kwargs):
        """Override the save method to set the option type."""
        self.set_option_type()
        super().save(*args, **kwargs)

    def set_option_type(self):
        """Set the option type. To be overridden in subclasses."""
        pass

    @property
    def premium_percentage(self):
        """Calculate the percentage of the premium received relative to the current stock price."""
        return round(((self.price_brl / self.asset.price_brl) * 100), 2 ) if self.asset.price_brl > 0 else 0

class Call(Option):
    """Model representing a call option."""

    def set_option_type(self):
        """Set the option type to CALL."""
        self.option_type = 'CALL'

class Put(Option):
    """Model representing a put option."""

    def set_option_type(self):
        """Set the option type to PUT."""
        self.option_type = 'PUT'



class PortfolioOption(models.Model):
    """Model representing a portfolio option."""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='portfolio_options')
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[
        ('SOLD', 'Sold'),
        ('BOUGHT', 'Bought'),
        ('CLOSED', 'Closed'),
        ('EXERCISED', 'Exercised'),
        ('EXPIRED', 'Expired')
    ], default='SOLD')
    quantity = models.FloatField() # Ex 900 é o mesmo para quantidade de opções e collaterals.
    price_brl = models.FloatField(help_text="Premium received per option.") # Ex: 0.32 preço da opção
    total_brl = models.FloatField(editable=False) # price_brl * quantity

    collateral = models.ForeignKey(PortfolioInvestment, on_delete=models.SET_NULL, null=True, blank=True) # ex: bbdc4 tenho 900 ações ou no caso de puts, cdb 10.000.

    collateral_total_price_brl = models.FloatField(null=True, blank=True, editable=False) # collateral.share_average_price_brl * quantity
    buyback_price = models.FloatField(default=0)  # Preço de recompra, se aplicável
    total_profit_brl = models.FloatField(default=0, editable=False)  # Total profit or loss for the transaction
    profit_percentage = models.FloatField(default=0, editable=False)  # Percentual de lucro ou perda
    exercise_price_brl = models.FloatField(default=0, editable=False)  # Preço de exercício, por ação.

    def save(self, *args, **kwargs):
        """Override the save method to calculate the total premium received."""
        self.total_brl = self.price_brl * self.quantity
        if self.collateral:
            self.collateral_total_price_brl = self.collateral.share_average_price_brl * self.quantity
        
        net_profit = self.calculate_net_profit()
        self.total_profit_brl = net_profit
        # Calculate profit percentage
        if self.total_brl > 0:
            self.profit_percentage = round((net_profit / (self.quantity * self.collateral.share_average_price_brl) * 100), 2)
        else:
            self.profit_percentage = 0

        super().save(*args, **kwargs)

    def calculate_net_profit(self):
        """Calculate net profit based on the status of the option."""
        if self.status == 'CLOSED':  # Option bought back and closed
            total_buyback_cost = self.buyback_price * self.quantity
            return self.total_brl - total_buyback_cost
        elif self.status == 'EXPIRED':  # Option expired
            return self.total_brl
        elif self.status == 'SOLD':  # Option sold but not yet closed
            return self.total_brl
        elif self.status == 'EXERCISED':  # Option exercised
            return 0
        else:
            return 0

    @property
    def option_price_today(self):
        """Calculate the market value of the option based on the current premium."""
        return self.option.price_brl

class PortfolioCalls(PortfolioOption):
    """Model representing a portfolio call option."""

    def calculate_net_profit(self):
        """Calculate net profit for call options based on the status of the option."""
        if self.status == 'EXERCISED':
            self.exercise_price_brl = self.option.price_brl + self.option.strike_price
            return 0
        return super().calculate_net_profit()

class PortfolioPuts(PortfolioOption):
    """Model representing a portfolio put option."""

    def calculate_net_profit(self):
        """Calculate net profit for put options based on the status of the option."""
        if self.status == 'EXERCISED':
            self.exercise_price_brl = self.option.strike_price - self.option.price_brl
            return 0
        return super().calculate_net_profit()


