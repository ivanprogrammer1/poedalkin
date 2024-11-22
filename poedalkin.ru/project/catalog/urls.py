from .views import CategoryListAPI, ProductListAPI, ProductObjectAPI, FiltersListAPI
from django.urls import path
urlpatterns = [
    path("api/catalog.getList", CategoryListAPI.as_view(), name="category.getList"),
    path("api/product.getList", ProductListAPI.as_view(), name="product.getList"),
    path('api/filters.getList', FiltersListAPI.as_view(), name="filters.getList"),
    path('api/product.get', ProductObjectAPI.as_view(), name="product.get"),
]