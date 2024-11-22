from rest_framework import serializers
from .models import Category, Product, Attribute, AttributeGroup, AttributeValue, AttributeName


# Category serializers
class CategorySerializer(serializers.ModelSerializer):

    has_children = serializers.SerializerMethodField()

    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'parent', 'title', 'thumbnail', 'active', 'has_children']

    def get_thumbnail(self, obj):
        thumbnail = obj.gallery.first()
        return "" if not thumbnail else thumbnail.get_image_full_url()

    def get_has_children(self, obj):
        return obj.get_descendants().filter(active=True).exists()

# Attributes serializers
class AttributeGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeGroup
        fields = ["slug", "title"]

class AttributeNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeName
        fields = ["slug", "title", "type_show"]

class AttributeValueSerializer(serializers.ModelSerializer):
    
    value = serializers.SerializerMethodField()
    
    class Meta:
        model = AttributeValue
        fields = ["slug", "value", "type_value"]

    def get_value(self, obj):
        return obj.get_value()

class AttributeSerializer(serializers.ModelSerializer):
    
    attr_name = serializers.SerializerMethodField()
    attr_value = serializers.SerializerMethodField()

    class Meta:
        model = Attribute
        fields = ["attr_name", "attr_value"]

    def get_attr_name(self, obj):
        return AttributeNameSerializer(obj.attribute_name).data

    def get_attr_value(self, obj):
        return AttributeValueSerializer(obj.attribute_value).data

# Products serializer
class ProductListSerializer(serializers.ModelSerializer):

    title = serializers.SerializerMethodField()

    base_attributes = serializers.SerializerMethodField()

    thumbnail = serializers.SerializerMethodField()

    is_collection = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'is_collection', 'thumbnail', 'price', 'old_price', 'discount', 'category', 'base_attributes']

    def get_title(self, obj):
        if(obj.collection):
            return obj.collection.title
        else:
            return obj.title

    def get_thumbnail(self, obj):

        thumbnail = obj.gallery.first()

        if(not thumbnail and obj.collection and obj.collection.image):
            thumbnail = obj.collection.get_image_full_url()
        elif(thumbnail):
            thumbnail = thumbnail.get_image_full_url()

        return "" if not thumbnail else thumbnail

    def get_base_attributes(self, obj):
        return obj.get_basic_attributes()

    def get_is_collection(self, obj):
        if(obj.collection):
            return True
        else:
            return False

class ProductObjectSerializer(serializers.ModelSerializer):

    attributes = serializers.SerializerMethodField()

    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'thumbnail', 'small_description', 'price', 'old_price', 'discount', 'category', 'attributes']

    def get_thumbnail(self, obj):
        thumbnail = obj.gallery.first()
        return "" if not thumbnail else thumbnail.get_image_full_url()

    def get_attributes(self, obj):
        result = AttributeSerializer(data=obj.attributes.all(), many=True)
        result.is_valid()
        return result.data
