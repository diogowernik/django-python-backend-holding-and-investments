from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name_plural = "Categorias"
        ordering = ('-name',)


class SubCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name_plural = "Áreas de Atuação"
        ordering = ('name',)

    def __str__(self):
        return "{}".format(self.name)

class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name_plural = "Tags"
        ordering = ('name',)

    def __str__(self):
        return "{}".format(self.name)
