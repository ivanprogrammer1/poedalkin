from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save
from mptt.models import MPTTModel, TreeForeignKey

from .catalog import Category
from catalog.managers import ProductManager
from django.core.exceptions import ValidationError
from ckeditor_uploader.fields import RichTextUploadingField
from slugify import slugify

def validate_positiveValue(value):
    if value < 0:
        raise ValidationError(F"Value {value} not positive")

def get_upload_collection_image(instance, filename):
    return F"collections/{slugify(instance.title)}/{filename}"

class CollectionProduct(models.Model):

    title = models.CharField(
        verbose_name="Имя",
        max_length=200
    )
    small_description = models.TextField(
        verbose_name="Описание",
        default="",
        blank=True
    )

    image = models.ImageField(verbose_name="Изображение", upload_to=get_upload_collection_image, null=True, blank=True)

    def get_image_full_url(self):
        return "http://poedalkin.ru" + self.image.url

    def __str__(self):
        return self.title

class Product(models.Model):

    objects = ProductManager()

    title = models.CharField(
        verbose_name="Имя",
        max_length=200
    )

    id_parse = models.CharField(max_length=200, default="", blank=True)

    description = RichTextUploadingField(verbose_name="Описание", blank=True, default="")

    small_description = models.TextField(verbose_name="Малое описание", blank=True, default="")

    price = models.FloatField(verbose_name="Цена", default=0, validators=[validate_positiveValue])

    old_price = models.FloatField(verbose_name="Старая цена", default=0, validators=[validate_positiveValue])

    discount = models.FloatField(verbose_name="Скидка", default=0, validators=[validate_positiveValue])

    active = models.BooleanField(
        verbose_name="Товар активен",
        default=False
    )

    collection = models.ForeignKey(
        CollectionProduct, 
        verbose_name="Коллекция", 
        related_name="children", 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True
    )

    category = models.ForeignKey(
        to=Category,
        verbose_name="Категория",
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def get_price_information(self):

        prices = {
            "price": self.price,
            "old_price": self.old_price,
            "discount": self.discount
        }

        return prices

    def get_active(self):
        return self.active

    def get_title(self):
        return self.title

    def get_parent(self):
        return self.parent

    def get_basic_attributes(self):
        attrs = {}
        for attr in self.attributes.filter(
            attribute_name__slug__in=[
                "uglevody",
                "kalorii",
                "zhiry",
                "belki"
            ]
        ):
            attrs[attr.attribute_name.title] = {
                "slug": attr.attribute_name.slug,
                "title": attr.attribute_name.title,
                "value": attr.attribute_value.get_value()
            }

        attrs_list = []
        for _, value in attrs.items():
            attrs_list.append(value)

        return attrs_list

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

def get_upload_productImage(instance, filename):
    return F"products/{instance.product.pk}/gallery/{filename}" 

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gallery", verbose_name="Товар")
    image = models.ImageField(verbose_name="Изображение", upload_to=get_upload_productImage)
    sort = models.PositiveIntegerField(verbose_name="Сортировка", default=0)
    main_image = models.BooleanField(verbose_name="Главное изображение", default=False,)

    def get_image_full_url(self):
        return "http://poedalkin.ru" + self.image.url

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Галерея"

@receiver(pre_save, sender = Product)
def product_pre_save(instance, sender, **kwargs):
    if(instance.old_price > 0):
        instance.discount = round(100 - (instance.price * 100 / instance.old_price), 2)
