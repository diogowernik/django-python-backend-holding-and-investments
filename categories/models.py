from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ('-name',)


class SubCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name_plural = "SubCategories"
        ordering = ('-name',)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        # White spaces organize who comes first
        verbose_name_plural = "SubCategories"
        ordering = ('-name',)
