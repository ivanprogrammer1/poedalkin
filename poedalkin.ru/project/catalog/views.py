from django.views import View
from django.http import JsonResponse

from rest_framework import mixins
from rest_framework import generics
from rest_framework.views import APIView

from .mixins import ListMixin
from .models import Category, Product
from catalog.filtration import ProductFilter
from .serializers import CategorySerializer, ProductListSerializer, ProductObjectSerializer

from django.db.models import Min

class CategoryListAPI(generics.GenericAPIView, ListMixin):
    serializer_class = CategorySerializer
    default_by_page = 6

    def get_queryset(self):
        category_id = self.request.GET.get("category_id", "")

        if(category_id):
            category = Category.objects.active(pk=category_id).first()
            queryset = category.get_descendants().filter(active=True)
        else:
            queryset = Category.objects.active().filter(parent=None)

        return queryset

    def get(self, request, *args, **kwargs):
        try:
            return JsonResponse({"success": True, "result": self.list(request, *args, **kwargs)})
        except:
            return JsonResponse({"success": False})

class ProductListAPI(generics.GenericAPIView, ListMixin):
    
    serializer_class = ProductListSerializer
    default_by_page = 36

    def get_queryset(self):
        category_id = self.request.GET.get("category_id", "")

        if(category_id):
            queryset = Product.objects.active(category__id=int(category_id))#.select_related("category").prefetch_related("attributes")
        else:
            queryset = Product.objects.active()#.select_related("category").prefetch_related("attributes")

        search = dict(self.request.GET)

        search.pop("page", None)
        search.pop("by_page", None)
        search.pop("category_id", None)

        search_attrs = {}

        for key, value in search.items():
            search_attrs[key] = value[0]

        filter_queryset = ProductFilter(queryset, search_attrs).filter_queryset()

        products_collection = filter_queryset.exclude(collection=None)
        products_pk = set(list(filter_queryset.filter(collection=None).values_list("pk", flat=True)))

        for prod_collection in products_collection:
            prod = prod_collection.collection.children.active().order_by("price").first()
            if(prod):
                products_pk.add(prod.pk)

        filter_queryset = Product.objects.active(pk__in = products_pk)

        return filter_queryset

    def get(self, request, *args, **kwargs):
        try:
            return JsonResponse({"success": True, "result": self.list(request, *args, **kwargs)})
        except:
            raise
            return JsonResponse({"success": False})

class FiltersListAPI(View):
    def get(self, request, *args, **kwargs):
        try:
            products = []
            category_id = request.GET.get("category_id", False)
            if(category_id):
                category_id = int(category_id)
                products = Product.objects.filter(category__id=category_id)
            else:
               products = Product.objects.all()

            return JsonResponse({
                "success": True,
                "result": ProductFilter(products).get_filters()
            })

        except:
            return JsonResponse({
                "success": False,
                "result": []
            })

class ProductObjectAPI(generics.GenericAPIView):
    
    serializer_class = ProductObjectSerializer

    def get_object(self):
        queryset = self.get_queryset()

        if(not queryset.exists()):
            return None

        return queryset.first()

    def get_queryset(self):
        product_id = self.request.GET.get("product_id", "")
        if(product_id):
            queryset = Product.objects.active(id=product_id)
        else:
            queryset = Product.objects.none()
        return queryset

    def get(self, request, *args, **kwargs):
        try:
            obj = self.get_object()

            result = None

            if(not obj.collection):
                result = {
                    "is_collection": False,
                    "object": self.get_serializer_class()(obj).data
                }
            else:
                collection = obj.collection
                list_serialization = self.get_serializer_class()(data=collection.children.all(), many=True)
                list_serialization.is_valid()
                result = {
                    "is_collection": True,
                    "image": collection.get_image_full_url() if collection.image else "",
                    "small_description": collection.small_description,
                    "title": collection.title,
                    "options": list_serialization.data
                }

            return JsonResponse({"success": True, "result": result})
        except:
            raise
            return JsonResponse({"success": False})