from django.contrib import admin

from .models import Client, Product, Order, OrderItem


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "total_purchases", "current_balance", "credit_limit", "current_debt")
    search_fields = ("name",)
    list_filter = ("credit_limit",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock")
    search_fields = ("name",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "sale_type", "created_at", "total_amount")
    list_filter = ("sale_type", "created_at")
    search_fields = ("client__name",)
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price")
    search_fields = ("order__id", "product__name")

