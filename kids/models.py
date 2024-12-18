from django.db import models
from portfolios.models import Portfolio, PortfolioInvestment, PortfolioDividend

class KidProfile(models.Model):
    belongs_to = models.ForeignKey(Portfolio, on_delete=models.CASCADE) # aqui é associado ao id do portfolio
    name = models.CharField(max_length=255)
    current_balance = models.FloatField(default=0)
    slug = models.CharField(max_length=255)
    age = models.IntegerField()
    image = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    LANGUAGE_CHOICES = [
        ('pt', 'Português'),
        ('en', 'Inglês'),
        ('fr', 'Francês'),
    ]
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='pt')

    CURRENCY_CHOICES = [
        ('R$', 'R$'),
        ('U$', 'U$'),
        ('€', '€'),
    ]
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='BRL')


    def get_portfolio_investments(self):
        return PortfolioInvestment.objects.filter(portfolio=self.belongs_to)
    
    def get_portfolio_dividends(self):
        return PortfolioDividend.objects.filter(portfolio=self.belongs_to)

    class Meta:
        verbose_name_plural = " KidProfiles"
    
    def __str__(self):
        return self.name

class KidsTransactions(models.Model):
    belongs_to = models.ForeignKey(KidProfile, on_delete=models.CASCADE, default=1, verbose_name='Pertence a')
    date = models.DateField(verbose_name='Data')
    description = models.CharField(max_length=255, verbose_name='Descrição')
    amount = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Valor')

    def __str__(self):
        return f"{self.date} - {self.description} - R$ {self.amount}"
    
    class Meta:
        abstract = True
        
class KidsEarns(KidsTransactions):
    CATEGORY_CHOICES = [
        ('aluguel', 'Aluguel'),
        ('missao', 'Missão'),
        ('presente', 'Presente'),
        ('outros', 'Outros'),
    ]
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES, verbose_name='Categoria')

    class Meta:
        verbose_name_plural = "KidsEarns"

    def save(self, *args, **kwargs):
        # Arredondando o valor para duas casas decimais
        self.amount = round(float(self.amount), 2)

        if self.pk:
            previous = KidsEarns.objects.get(pk=self.pk)
            amount_diff = round(float(self.amount) - float(previous.amount), 2)
            self.belongs_to.current_balance = round(self.belongs_to.current_balance + amount_diff, 2)
        else:
            self.belongs_to.current_balance = round(self.belongs_to.current_balance + float(self.amount), 2)

        self.belongs_to.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.belongs_to.current_balance = round(self.belongs_to.current_balance - float(self.amount), 2)
        self.belongs_to.save()
        super().delete(*args, **kwargs)


class KidsExpenses(KidsTransactions):
    CATEGORY_CHOICES = [
        ('doces', 'Doces'),
        ('comidas', 'Comidas'),
        ('brinquedos', 'Brinquedos'),
        ('outros', 'Outros'),
    ]
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES, verbose_name='Categoria')

    class Meta:
        verbose_name_plural = "KidsExpenses"

    def save(self, *args, **kwargs):
        # Arredondando o valor para duas casas decimais
        self.amount = round(float(self.amount), 2)

        if self.pk:
            previous = KidsExpenses.objects.get(pk=self.pk)
            amount_diff = round(float(self.amount) - float(previous.amount), 2)
            self.belongs_to.current_balance = round(self.belongs_to.current_balance - amount_diff, 2)
        else:
            self.belongs_to.current_balance = round(self.belongs_to.current_balance - float(self.amount), 2)

        self.belongs_to.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.belongs_to.current_balance = round(self.belongs_to.current_balance + float(self.amount), 2)
        self.belongs_to.save()
        super().delete(*args, **kwargs)

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

class KidsButtons(models.Model):
    belongs_to = models.OneToOneField(KidProfile, on_delete=models.CASCADE, related_name='dashboard_buttons')
    show_dividends = models.BooleanField(default=True)
    show_quests = models.BooleanField(default=True)
    show_earnings = models.BooleanField(default=True)
    show_expenses = models.BooleanField(default=True)
    show_games = models.BooleanField(default=False)
    show_events = models.BooleanField(default=True)
    show_goals = models.BooleanField(default=False)
    show_education = models.BooleanField(default=False)
    show_growth = models.BooleanField(default=True)
    show_banks = models.BooleanField(default=True)
    show_explore = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "KidsButtons"