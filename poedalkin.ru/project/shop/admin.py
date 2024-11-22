from django.contrib import admin
from .models import Order, OrderItem, OrderStatusLog, STATUSES
from django import forms

# Register your models here.
class OrderLogItemInline(admin.StackedInline):
    model = OrderStatusLog
    extra = 0

class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0

class OrderFormAdmin(forms.ModelForm):

    EMPTY_CHOICE = [('', '-----------')]

    change_status_field = forms.fields.ChoiceField(
        choices= EMPTY_CHOICE + STATUSES,
        required=False,
        label="Заменить статус заказа"
    )

    class Meta:
        fields = [
            "change_status_field",
            "user",
            "subtotal",
            "work_comment",
            "phone",
            "street",
            "house",
            "apartment",
            "entrance",
            "floor",
            "door_code",
            "comment"
        ]
        model = Order



class OrderAdmin(admin.ModelAdmin):
    form = OrderFormAdmin
    model = Order
    inlines = [OrderItemInline, OrderLogItemInline]

    def save_model(self, request, obj, form, change):
        data = form.cleaned_data
        if(data.get("change_status_field")):
            obj.change_status(data.get("change_status_field"))
        super().save_model(request, obj, form, change)

admin.site.register(Order, OrderAdmin)