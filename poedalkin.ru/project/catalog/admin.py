from django.contrib import admin
from .models import Category, Attribute, AttributeGroup, AttributeName, AttributeValue, Product, ProductImage, \
    CategoryImage, CollectionProduct

# Товар
class ProductImageInline(admin.StackedInline):
    model = ProductImage

class AttributeProductInline(admin.StackedInline):
    model = Attribute
    fields = ('attribute_group', 'attribute_name', 'attribute_value')

class ProductAdminModel(admin.ModelAdmin):
    model = Product
    inlines = [ProductImageInline, AttributeProductInline, ]

# Категория
class CategoryImageInline(admin.StackedInline):
    model = CategoryImage

class CategoryAdminModel(admin.ModelAdmin):
    model = Category
    inlines = [CategoryImageInline, ]

# Атрибуты
class AttributeAdminModel(admin.ModelAdmin):
    model = Attribute

class AttributeGroupAdminModel(admin.ModelAdmin):
    model = AttributeGroup
    prepopulated_fields = {
        "slug": ("title", )
    }

class AttributeNameAdminModel(admin.ModelAdmin):
    model = AttributeName
    prepopulated_fields = {
        "slug": ("title", )
    }

class AttributeValueAdminModel(admin.ModelAdmin):
    model = AttributeValue

admin.site.register(CollectionProduct)

admin.site.register(Product, ProductAdminModel)

admin.site.register(Category, CategoryAdminModel)

admin.site.register(Attribute, AttributeAdminModel)

admin.site.register(AttributeGroup, AttributeGroupAdminModel)

admin.site.register(AttributeName, AttributeNameAdminModel)

admin.site.register(AttributeValue, AttributeValueAdminModel)

