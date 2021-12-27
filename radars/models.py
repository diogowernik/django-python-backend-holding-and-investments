from django.db import models
from django.contrib.auth.models import User
from arquivo.holding_backend.core.models import Portfolio
from investments.models import Asset

# Create your models here.

class Radar(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=255)

    def __str__(self):
        return "{}/{}".format(self.place, self.name)
    
    class Meta:
        verbose_name_plural = "   Radars"


class RadarItem(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    radar = models.ForeignKey(Radar, on_delete=models.CASCADE, related_name="menu_items")
    name = models.CharField(max_length=255)
    # description = models.TextField(blank=True)
    # price = models.IntegerField(default=0)
    # image = models.CharField(max_length=255)
    # is_available = models.BooleanField(default=True)

    def __str__(self):
        return "{}/{}".format(self.radar, self.name)




# class RadarAsset(models.Model):
#     radar = models.ForeignKey(Radar, on_delete=models.CASCADE)
#     asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    

#     def __str__(self):
#         return '  {}  |  {}  '.format(self.asset, self.radar)

#     class Meta:
#         verbose_name_plural = "  Radar Asset"