from django.urls import path
from .views import *

urlpatterns = [
    path("api/cart.add", ChangeBasket.as_view(), name="cart.add"),
    path("api/cart.get", GetBasket.as_view(), name="card.get"),

    path("api/order.add", CreateOrder.as_view(), name="order.add"),
    path("api/order.getList", OrderListAPI.as_view(), name="order.getList"),
    path("api/order.get", OrderObjectAPI.as_view(), name="order.get"),
    path("api/coordinates.get", CoordinatesAPI.as_view(), name="coordinates.get")
]