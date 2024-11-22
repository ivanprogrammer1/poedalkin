from rest_framework import serializers
from .models import Basket, BasketItem, Order, OrderItem, OrderStatusLog

class BasketItemSerializer(serializers.ModelSerializer):

    title = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    sum = serializers.SerializerMethodField()
    old_price = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = BasketItem
        fields = ['product', 'count', 'title', "price", "old_price", "discount", "image", "sum"]

    def get_image(self, obj):

        if(obj.product.collection):
            return obj.product.collection.get_image_full_url()
        else:
            image = obj.product.gallery.all().order_by("main_image", "sort").first()

            if(image):
                return image.get_image_full_url()

        return ""

    def get_title(self, obj):
        return obj.product.title

    def get_sum(self, obj):
        return obj.sum

    def get_price(self, obj):
        return obj.price

    def get_old_price(self, obj):
        return obj.old_price

    def get_discount(self, obj):
        return obj.discount

class BasketSerializer(serializers.ModelSerializer):

    items = serializers.SerializerMethodField()

    count = serializers.SerializerMethodField()

    sum = serializers.SerializerMethodField()

    class Meta:
        model = Basket
        fields = ['items', 'count', "sum", ]

    def get_sum(self, obj):
        return obj.sum

    def get_items(self, obj):
        result = BasketItemSerializer(data=obj.products.all(), many=True)
        result.is_valid()
        return result.data

    def get_count(self, obj):
        return obj.products.count()

class OrderStatusSerializer(serializers.ModelSerializer):

    datetime = serializers.SerializerMethodField()

    class Meta:
        model = OrderStatusLog
        fields = ['status', 'datetime']

    def get_datetime(self, obj):
        return obj.datetime.strftime("%d.%m.%Y %H:%M")

class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ["pk", "product", "title", "cost", "total", "count", "title"]

class OrderListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['pk', 'status', 'subtotal']

class OrderSerializer(serializers.ModelSerializer):

    items = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'pk', 
            'status',
            'subtotal', 
            'items', 
            'history', 
            'phone', 
            'street', 
            'house', 
            'apartment',
            'entrance', 
            'floor', 
            'door_code', 
            'comment',
            'count'
        ]

    def get_count(self, obj):
        return obj.count

    def get_items(self, obj):
        result = OrderItemSerializer(data=obj.items.all(), many=True)
        result.is_valid()
        return result.data

    def get_history(self, obj):
        result = OrderStatusSerializer(data=obj.history.all(), many=True)
        result.is_valid()
        return result.data