from django.db import models

class CategoryManager(models.Manager):
    def active(self, **filters):
        return self.filter(active=True, **filters)

class ProductManager(models.Manager):
    def active(self, **filters):
        return self.filter(active=True, price__gt=0, **filters)