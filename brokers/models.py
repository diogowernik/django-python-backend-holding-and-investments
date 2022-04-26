from django.db import models

# Create your models here.


class Broker(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        # White spaces organize who comes first
        verbose_name_plural = " Brokers"
