from django.shortcuts import render
from django.views import View

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import *

from user.models import SessionOAuth
from user.utils import get_user, get_basket

from django.http import JsonResponse
from catalog.models import Product

from .serializers import BasketSerializer, BasketItemSerializer, OrderSerializer, OrderListSerializer

from rest_framework import generics
from catalog.mixins import ListMixin
from project.settings import GEOOBJECTS_FILEPATH 

import json
import re

REGEX_NUMBER_EXPRESSION = r"^(\+7|7|8)?[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$"


@method_decorator(csrf_exempt, name='dispatch')
class ChangeBasket(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        return 

    def post(self, *args, **kwargs):
        
        try:
            user = get_user(self.request)
        except SessionOAuth.SessionException as e:
            return JsonResponse({"success": False, "result": str(e)})

        basket = get_basket(user)

        product_id = self.request.GET.get("product_id", None)
        product_count = self.request.GET.get("product_count", None)

        if(not product_id or not product_count or not str.isdigit(product_count)):
            return JsonResponse(
                {
                    "success": False,
                    "result": "Неправильные данные"
                }
            )

        product = Product.objects.active(pk=product_id).first()

        if(not product):
            return JsonResponse(
                {
                    "success": False,
                    "result": "Неправильные данные"
                }
            )

        try:
            basket.change_item(product, int(product_count), False, True)
        except:
            return JsonResponse({
                "success": False,
                "result": "Неправильные данные"
            })

        return JsonResponse({
            "success": True,
            "result": BasketSerializer(basket).data
        })

class GetBasket(View):
    def get(self, *args, **kwargs):

        try:
            user = get_user(self.request)
        except SessionOAuth.SessionException as e:
            return JsonResponse({"success": False, "result": str(e)})

        basket = get_basket(user)
        
        return JsonResponse({"success": True, "result": BasketSerializer(basket).data})

class CreateOrder(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        
        try:
            user = get_user(self.request)
        except SessionOAuth.SessionException as e:
            return JsonResponse({"success": False, "result": str(e)})

        errors = []

        basket = get_basket(user)

        order = Order()

        if(basket.products.all().count() == 0):
            errors += [{
                "name": "basket_count",
                "error": "Корзина не должна быть пустой"
            }]

        dataJSON = json.loads(self.request.body)

        phone = dataJSON.get("phone", "")
        street = dataJSON.get("street", "")
        house = dataJSON.get("house", "")
        apartment = dataJSON.get("apartment", "")
        entrance = dataJSON.get("entrance", "")
        floor = dataJSON.get("floor", "")
        door_code = dataJSON.get("door_code", "")
        comment = dataJSON.get("comment", "")

        errors = self.check_errors("phone", phone, errors)
        errors = self.check_errors("street", street, errors)
        errors = self.check_errors("house", house, errors)
        errors = self.check_errors("apartment", apartment, errors)
        errors = self.check_errors("entrance", entrance, errors)
        errors = self.check_errors("floor", floor, errors)
        errors = self.check_errors("door_code", door_code, errors)
        errors = self.check_errors("comment", comment, errors)

        if(len(errors) == 0):
            order.user = user
            order.phone = phone
            order.street = street
            order.house = house
            order.apartment = apartment
            order.entrance = entrance
            order.floor = floor
            order.door_code = door_code
            order.comment = comment

            basketItems = basket.products.all()
            orderItems = []            

            sum = 0

            for item in basketItems:
                sum += item.sum
                orderItems.append(OrderItem(
                    order=order,
                    product=item.product,
                    price=item.price,
                    sum=item.sum,
                    count=item.count
                ))

            order.subtotal = sum
            order.save()

            for item in orderItems:
                item.save()

            order.save()
            order.save_log()
            basket.clear_cart()

            return JsonResponse({
                "success": True,
                "result": OrderSerializer(order).data
            })

        else:
            return JsonResponse({
                "success": False,
                "result": {
                    "errors": errors
                }
            })

    def check_errors(self, key, value, errors):
        if(
            key in ["phone", "street", "house", "apartment", "entrance", "floor"]
        ):
            if(value == ""):
                errors += [{
                    "name": key,
                    "error": "Поле должно быть заполненным"
                }]
            elif(key == "phone"):
                pattern = re.compile(REGEX_NUMBER_EXPRESSION)
                if(not pattern.match(value)):
                    errors += [{
                        "name": key,
                        "error": "Поле заполнено неправильно"
                    }]

        return errors

class OrderListAPI(generics.GenericAPIView, ListMixin):
    serializer_class = OrderListSerializer
    default_by_page = 36

    def get_queryset(self, *args, **kwargs):
        try:
            user = get_user(self.request)
        except SessionOAuth.SessionException as e:
            return JsonResponse({"success": False, "result": str(e)})

        return user.orders.all().order_by("-id")

    def get(self, request, *args, **kwargs):
        try:
            return JsonResponse({"success": True, "result": self.list(request, *args, **kwargs)})
        except:
            return JsonResponse({"success": False})


class OrderObjectAPI(View):
    def get(self, *args, **kwargs):
        try:
            user = get_user(self.request)
        except SessionOAuth.SessionException as e:
            return JsonResponse({"success": False, "result": str(e)})

        order_key = self.request.GET.get("order_id", "")

        order = user.orders.filter(pk=order_key).first()

        if(not order):
            return JsonResponse({"success": False, "result": "Заказ с таким номером отсутствует"})

        return JsonResponse({
            "success": True,
            "result": OrderSerializer(order).data
        })


class CoordinatesAPI(View):
    def get(self, *args, **kwargs):

        mapObjectData = {}
        with open(GEOOBJECTS_FILEPATH, "r") as f:
            mapObjectData = json.loads(f.read())

        return JsonResponse({
            "success": True,
            "result": {
                "mapObjectData": mapObjectData,
                "mapCenterCoordinates": [30.264981955459618, 59.9567962610097],
                "mapZoom": 9
            }
        })