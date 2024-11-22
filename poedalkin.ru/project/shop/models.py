from django.db import models
from user.models import User
from catalog.models import Product
from django.utils import timezone
from .model_mixins import AddressFields

CREATED = 'created'
PROCESSED = 'processed'
CANCELED = 'canceled'
DELIVERY = "delivery"
DELIVERED = 'delivered'
FINISHED = "finished"

STATUSES = [
    (CREATED, "Заказ создан"),
    (PROCESSED, "Заказ обрабатывается"),
    (CANCELED, "Заказ отменён"),
    (DELIVERY, "Заказ у курьера"),
    (DELIVERED, "Успешно доставлен"),
    (FINISHED, "Заказ закончен")
]

class Basket(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="basket")

    class BasketException(Exception):
        pass

    class BasketItemCountException(BasketException):
        pass

    def clear_cart(self):
        self.products.all().delete()

    @property
    def sum(self):
        sum = 0

        for item in self.products.all():
            sum += item.sum

        return sum

    def change_item(self, product, count, sum=False, unsuitable_del=False):
        bsk_product = self.products.filter(product=product).first()

        if(not bsk_product):
            bsk_product = BasketItem(basket=self, product=product)

        if(sum):
            bsk_product.count += count
        else:
            bsk_product.count = count
            
        if(bsk_product.count <= 0):
            
            if(unsuitable_del):
                bsk_product.delete()
                return
            else:
                raise self.BasketItemCountException()

        bsk_product.save()

class BasketItem(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name="products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="baskets")
    count = models.PositiveIntegerField(default=1)

    @property
    def discount(self):
        return self.product.get_price_information()["discount"]

    @property
    def old_price(self):
        return self.product.get_price_information()["old_price"]

    @property
    def price(self):
        return self.product.get_price_information()["price"]

    @property
    def sum(self):        
        return self.product.get_price_information()["price"] * self.count

class Order(AddressFields):
    status = models.CharField(max_length=200, choices=STATUSES, default=CREATED)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="orders")
    subtotal = models.FloatField()

    work_comment = models.TextField(default="", blank=True)

    @property
    def count(self):
        count = 0
        for item in self.items.all():
            count += item.count
        return count

    def save_log(self):
        OrderStatusLog.save_log(self)

    def change_status(self, status):
        self.status = status
        self.save()
        OrderStatusLog.save_log(self)

class OrderStatusLog(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="history")
    status = models.CharField(max_length=200, choices=STATUSES, default=CREATED)
    datetime = models.DateTimeField()

    @classmethod
    def save_log(cls, order_obj):
        cls(
            order=order_obj,
            status=order_obj.status,
            datetime=timezone.now()
        ).save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField()
    sum = models.FloatField()
    count = models.PositiveIntegerField()

    @property
    def title(self):
        return self.product.title

    @property
    def total(self):
        return self.sum

    @property
    def cost(self):
        return self.price

class OrderAddressUser(AddressFields):
    user = models.ForeignKey(User, on_delete=models.CASCADE)