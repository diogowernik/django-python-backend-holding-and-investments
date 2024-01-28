from django.db import models
from portfolios.models import Portfolio, PortfolioInvestment, PortfolioDividend

class KidProfile(models.Model):
    belongs_to = models.ForeignKey(Portfolio, on_delete=models.CASCADE) # aqui é associado ao id do portfolio
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
    
    def __str__(self):
        return self.name

class KidsQuest(models.Model):
    belongs_to = models.ForeignKey(KidProfile, on_delete=models.CASCADE)
    quest_key = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=255)
    story = models.TextField()
    mission = models.CharField(max_length=255)
    mission_details = models.TextField()
    reward = models.CharField(max_length=255)  # Use CharField já que a recompensa pode ser não-numérica (como "o lucro da venda")
    image = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "KidsQuests"
