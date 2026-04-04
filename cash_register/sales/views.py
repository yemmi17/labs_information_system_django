from decimal import Decimal

from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.shortcuts import render

from .models import Sale


def profit_by_group(request):
    """
    Сумма прибыли по каждой группе товаров:
    Σ ((sale_price − purchase_price) × quantity).
    """
    line_profit = ExpressionWrapper(
        (F("sale_price") - F("purchase_price")) * F("quantity"),
        output_field=DecimalField(max_digits=16, decimal_places=2),
    )
    rows = (
        Sale.objects.values("product_group__name")
        .annotate(total_profit=Sum(line_profit))
        .order_by("product_group__name")
    )
    total = sum((r["total_profit"] or Decimal("0")) for r in rows)
    context = {
        "rows": rows,
        "total_profit": total,
    }
    return render(request, "sales/profit_by_group.html", context)


def sale_list(request):
    sales = Sale.objects.select_related("product_group").all()
    return render(request, "sales/sale_list.html", {"sales": sales})
