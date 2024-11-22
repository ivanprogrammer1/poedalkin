from django.db import models

class AddressFields(models.Model):
    phone = models.CharField(max_length=200, blank=True, default="")
    street = models.CharField(max_length=200, blank=True, default="")
    house = models.CharField(max_length=200, blank=True, default="")
    apartment = models.CharField(max_length=200, blank=True, default="")
    entrance = models.CharField(max_length=200, blank=True, default="")
    floor = models.CharField(max_length=200, blank=True, default="")
    door_code = models.CharField(max_length=200, blank=True, default="")
    comment = models.CharField(max_length=200, blank=True, default="")

    class Meta:
        abstract = True