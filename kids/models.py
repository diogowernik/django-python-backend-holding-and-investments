from django.db import models
from portfolios.models import Portfolio, PortfolioInvestment, PortfolioDividend

class KidProfile(models.Model):
    belongs_to = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    age = models.IntegerField()
    image = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_portfolio_investments(self):
        return PortfolioInvestment.objects.filter(portfolio=self.belongs_to)
    
    def get_portfolio_dividends(self):
        return PortfolioDividend.objects.filter(portfolio=self.belongs_to)

    class Meta:
        verbose_name_plural = " KidProfiles"