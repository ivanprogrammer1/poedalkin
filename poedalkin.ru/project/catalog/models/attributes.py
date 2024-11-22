from slugify import slugify
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

from .product import Product

class AttributeGroup(models.Model):

    slug = models.SlugField(
        verbose_name="Путь",
        unique=True
    )

    title = models.CharField(
        verbose_name="Имя",
        max_length=200
    )

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = "Группа атрибутов"
        verbose_name_plural = "Группы атрибутов"

class AttributeName(models.Model):

    RANGE = "range"
    DICT = "dict"
    RADIO = "radio"

    TypeChoices = [
        (RANGE, 'Диапазон'),
        (DICT, "Чекбоксы"),
        (RADIO, 'Радиокнопки')
    ]

    type_show = models.CharField(
        verbose_name="Тип отображения",
        choices=TypeChoices,
        max_length=100,
        default=DICT
    )

    slug = models.SlugField(
        verbose_name="Путь",
        unique=True
    )

    title = models.CharField(
        verbose_name="Имя",
        max_length=200
    )

    def get_slug(self):
        return self.slug

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = "Имя атрибута"
        verbose_name_plural = "Имена атрибутов"

class AttributeValue(models.Model):

    DIGIT = "digit"
    LETTERS = "letters"

    TypeChoices = [
        (DIGIT, 'Цифровое'),
        (LETTERS, 'Знаковое')
    ]

    slug = models.SlugField(
        verbose_name="Путь",
        unique=True,
        editable=False
    )

    text_value = models.CharField(
        verbose_name="Знаковое значение",
        max_length=200,
        default="",
        blank=True
    )

    digitValue = models.DecimalField(
        verbose_name="Цифровое значение",
        default=0,
        max_digits=12,
        decimal_places=6,
        blank=True
    )

    type_value = models.CharField(
        verbose_name="Тип значения",
        choices=TypeChoices,
        max_length=100,
        default=LETTERS
    )

    def get_slug(self):
        return self.slug

    def get_value(self):
        if(self.type_value == self.LETTERS):
            return self.text_value
        else:
            return float(self.digitValue)

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = "Значение атрибута"
        verbose_name_plural = "Значения атрибутов"

class Attribute(models.Model):

    attribute_group = models.ForeignKey(
        AttributeGroup,
        verbose_name="Группа атрибута",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attributes"
    )

    attribute_name = models.ForeignKey(
        AttributeName,
        verbose_name="Имя атрибута",
        on_delete=models.CASCADE,
        related_name="attributes"
    )

    attribute_value = models.ForeignKey(
        AttributeValue,
        verbose_name="Значение атрибута",
        on_delete=models.CASCADE,
        related_name="attributes"
    )

    product = models.ForeignKey(
        to=Product,
        verbose_name="Продукт",
        related_name="attributes",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Атрибут"
        verbose_name_plural = "Атрибуты"

@receiver(pre_save, sender=AttributeValue)
def attribute_value_pre_save(instance, sender, **kwargs):
    if(instance.type_value == instance.DIGIT):
        instance.slug = slugify(str(instance.digitValue))
    else:
        if(not instance.text_value):
            raise Exception("Значение не заполнено")
        instance.slug = slugify(str(instance.text_value))

@receiver(post_save, sender=AttributeName)
def attribute_value_post_save(instance, sender, **kwargs):
    for attr in instance.attributes.all():
        attr.save()

@receiver(post_save, sender=AttributeValue)
def attribute_value_post_save(instance, sender, **kwargs):
    for attr in instance.attributes.all():
        attr.save()