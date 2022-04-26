from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name_plural = "   Categories"  # White spaces organize who comes first


class SetorFii(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        # White spaces organize who comes first
        verbose_name_plural = "   Fiis Categories"


class SetorCrypto(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        # White spaces organize who comes first
        verbose_name_plural = "   Crypto Categories"
