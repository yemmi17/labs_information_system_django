from django.contrib import admin

from .models import ProductGroup, Sale

admin.site.site_header = "Кассовые продажи"
admin.site.site_title = "Касса"


@admin.register(ProductGroup)
class ProductGroupAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        "product_name",
        "product_group",
        "quantity",
        "sale_price",
        "purchase_price",
        "discount",
        "line_profit_display",
    )
    list_filter = ["product_group"]
    search_fields = ["product_name"]
    autocomplete_fields = ["product_group"]

    @admin.display(description="прибыль по строке")
    def line_profit_display(self, obj: Sale) -> str:
        return f"{obj.line_profit:.2f}"
