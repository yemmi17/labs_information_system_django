from django import forms
from django.forms import inlineformset_factory

from .models import Client, Product, Order, OrderItem


class ClientSearchForm(forms.Form):
    name = forms.CharField(
        label="Имя клиента",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
    )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "price", "stock"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }

    def clean(self):
        cleaned = super().clean()
        name = cleaned.get("name")
        price = cleaned.get("price")
        stock = cleaned.get("stock")

        if not name:
            self.add_error("name", "Наименование товара обязательно.")
        if price is not None and price <= 0:
            self.add_error("price", "Цена должна быть больше нуля.")
        if stock is not None and stock < 0:
            self.add_error("stock", "Количество не может быть отрицательным.")
        return cleaned


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["client", "sale_type"]
        widgets = {
            "client": forms.Select(attrs={"class": "form-select"}),
            "sale_type": forms.Select(attrs={"class": "form-select"}),
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-select product-select"}),
            "quantity": forms.NumberInput(
                attrs={"class": "form-control quantity-input", "step": "0.01"}
            ),
        }


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=3,
    can_delete=True,
)

