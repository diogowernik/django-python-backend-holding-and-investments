from django.core.exceptions import ValidationError
from django.db import models
from portfolios.models import Portfolio, PortfolioInvestment
from categories.models import Category
from investments.models import Asset

from django.db.models import Sum

class Radar(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)

    # Campo calculado automaticamente quando acessado
    @property
    def portfolio_total_value(self):
        return round(self.portfolio.portfolioinvestment_set.aggregate(Sum('total_today_brl'))['total_today_brl__sum'], 2) or 0

    def __str__(self):
        return self.name + ' - ' + str(self.portfolio_total_value)


class RadarCategory(models.Model):
    radar = models.ForeignKey(Radar, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    ideal_category_percentage = models.FloatField(default=0)

    # Campos calculados automaticamente quando acessados
    @property
    def category_total_value(self):
        return PortfolioInvestment.objects.filter(portfolio=self.radar.portfolio, asset__category=self.category).aggregate(Sum('total_today_brl'))['total_today_brl__sum'] or 0
    
    @property
    def category_percentage_on_portfolio(self):
        if self.radar.portfolio_total_value != 0:  # to avoid division by zero
            return self.category_total_value / self.radar.portfolio_total_value 
        else:
            return 0

    @property
    def delta_ideal_actual_percentage(self):
        delta = self.ideal_category_percentage - self.category_percentage_on_portfolio
        # o app só recomendará compra para rebalancear, por isso não faz sentido ter um valor negativo
        return delta if delta > 0 else 0

    def __str__(self):
        return self.category.name + ' - ' + str(self.category_total_value)
    
    def clean(self):
        if not 0 <= self.ideal_category_percentage <= 1:
            if self.ideal_category_percentage > 1:
                # Calcular a porcentagem a mais que excede 100%
                percentage_excess = (self.ideal_category_percentage - 1) * 100
                raise ValidationError(f"A porcentagem ideal da categoria deve ser entre 0 e 1 (representando de 0% a 100%). Atualmente, a porcentagem ideal excede 100% em {percentage_excess}%.")
            else:
                # Calcular a porcentagem que falta para atingir 100%
                percentage_missing = (1 - self.ideal_category_percentage) * 100
                raise ValidationError(f"A porcentagem ideal da categoria deve ser entre 0 e 1 (representando de 0% a 100%). Atualmente, faltam {percentage_missing}% para completar 100%.")

    class Meta:
        unique_together = ['radar', 'category']

    
class RadarAsset(models.Model):
    radar = models.ForeignKey(Radar, on_delete=models.CASCADE, default=1)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    radar_category = models.ForeignKey(RadarCategory, on_delete=models.CASCADE, editable=False, null=True, blank=True)

    ideal_asset_percentage_on_category = models.FloatField(default=0.1)
    ideal_asset_percentage_on_portfolio = models.FloatField(default=0, editable=False)

    # Campos calculados automaticamente quando acessados
    @property
    def portfolio_investment_total_value(self):
        return PortfolioInvestment.objects.filter(portfolio=self.radar.portfolio, asset=self.asset).aggregate(Sum('total_today_brl'))['total_today_brl__sum'] or 0 

    @property
    def portfolio_investment_percentage_on_category(self):
        if self.radar_category and self.radar_category.category_total_value != 0:
            return self.portfolio_investment_total_value / self.radar_category.category_total_value
        else:
            return 0

    @property
    def portfolio_investment_percentage_on_portfolio(self):
        if self.radar.portfolio_total_value != 0:
            return self.portfolio_investment_total_value / self.radar.portfolio_total_value
        else:
            return 0

    @property
    def delta_ideal_actual_percentage_on_category(self):
        delta = self.ideal_asset_percentage_on_category - self.portfolio_investment_percentage_on_category
        return delta if delta > 0 else 0

    @property
    def delta_ideal_actual_percentage_on_portfolio(self):
        delta = self.ideal_asset_percentage_on_portfolio - self.portfolio_investment_percentage_on_portfolio
        return delta if delta > 0 else 0

    def __str__(self):
        return self.asset.ticker + ' - ' + str(self.portfolio_investment_total_value)
    
    def clean(self):
        if not 0 <= self.ideal_asset_percentage_on_category <= 1:
            raise ValidationError("A porcentagem ideal do ativo na categoria deve ser entre 0 e 1 (representando de 0% a 100%)")
    
        if not 0 <= self.ideal_asset_percentage_on_portfolio <= 1:
            raise ValidationError("A porcentagem ideal do ativo no portfólio deve ser entre 0 e 1 (representando de 0% a 100%)")

    class Meta:
        unique_together = ['radar', 'asset']
