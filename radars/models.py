from django.db import models
from django.contrib.auth.models import User
from portfolios.models import Portfolio
from investments.models import Asset

# Create your models here.

class Radar(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="radars")
    name = models.CharField(max_length=255)

    def __str__(self):
        return "{}/{}".format(self.portfolio, self.name)
    
    class Meta:
        verbose_name_plural = "   Radars"


class RadarItem(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    radar = models.ForeignKey(Radar, on_delete=models.CASCADE, related_name="radar_items")
    name = models.CharField(max_length=255)

    def __str__(self):
        return "{}/{}".format(self.radar, self.name)
