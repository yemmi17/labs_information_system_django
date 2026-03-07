from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, F
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .forms import (
    ClientSearchForm,
    ProductForm,
    OrderForm,
    OrderItemFormSet,
)
from .models import Client, Product, Order


def home(request):
    return render(request, "sales/home.html")


def client_search_view(request):
    form = ClientSearchForm(request.GET or None)
    client = None

    if form.is_valid():
        name = form.cleaned_data["name"]
        client = (
            Client.objects.filter(name__icontains=name)
            .order_by("name")
            .first()
        )
        if not client:
            messages.info(request, "Клиент с таким именем не найден.")

    return render(request, "sales/client_search.html", {"form": form, "client": client})


def product_list_view(request):
    products = Product.objects.all().order_by("name")

    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Товар добавлен/обновлён.")
            return redirect("sales:product_list")
        else:
            messages.error(
                request,
                "Проверьте строки с пустым товаром, нулевой ценой или нулевым количеством.",
            )
    else:
        form = ProductForm()

    return render(
        request,
        "sales/product_list.html",
        {"products": products, "form": form},
    )


@transaction.atomic
def order_create_view(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            client = order.client
            order.save()
            items = formset.save(commit=False)

            total = Decimal("0")
            for item in items:
                if not item.product:
                    continue
                product = item.product
                item.price = product.price
                line_total = item.quantity * item.price
                total += line_total

                if item.quantity > product.stock and order.sale_type != Order.SaleType.BARTER:
                    messages.error(
                        request,
                        f"Количество товара '{product.name}' превышает остаток.",
                    )
                    transaction.set_rollback(True)
                    return render(
                        request,
                        "sales/order_create.html",
                        {"form": form, "formset": formset},
                    )

            if order.sale_type == Order.SaleType.CASH:
                client.total_purchases += total

            elif order.sale_type == Order.SaleType.NONCASH:
                client.total_purchases += total
                client.current_balance -= total

            elif order.sale_type == Order.SaleType.CREDIT:
                if client.current_balance > 0:
                    used = min(client.current_balance, total)
                    client.current_balance -= used
                    total -= used

                client.total_purchases += total
                client.current_debt += total

                if client.current_debt > client.credit_limit:
                    messages.error(
                        request,
                        "Сумма покупки превышает доступный кредитный лимит клиента.",
                    )
                    transaction.set_rollback(True)
                    return render(
                        request,
                        "sales/order_create.html",
                        {"form": form, "formset": formset},
                    )

            elif order.sale_type == Order.SaleType.BARTER:
                pass

            elif order.sale_type == Order.SaleType.OFFSET:
                client.current_debt -= total
                if client.current_debt < 0:
                    client.current_debt = 0

            for item in items:
                if not item.product:
                    continue
                product = item.product

                if order.sale_type in (
                    Order.SaleType.CASH,
                    Order.SaleType.NONCASH,
                    Order.SaleType.CREDIT,
                ):
                    product.stock -= item.quantity
                elif order.sale_type == Order.SaleType.OFFSET:
                    product.stock += item.quantity

                product.save()
                item.order = order
                item.save()

            client.save()

            if client.credit_usage_ratio >= 0.9:
                messages.warning(
                    request,
                    "Внимание: текущий долг клиента близок к потолку кредита.",
                )

            messages.success(request, "Заказ успешно создан.")
            return redirect(reverse("sales:order_detail", args=[order.id]))
    else:
        form = OrderForm()
        formset = OrderItemFormSet()

    return render(request, "sales/order_create.html", {"form": form, "formset": formset})


def order_detail_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, "sales/order_detail.html", {"order": order})


def client_orders_report_view(request):
    orders = (
        Order.objects.annotate(
            order_total=Sum(F("items__quantity") * F("items__price"))
        )
        .select_related("client")
        .order_by("client__name", "created_at")
    )

    return render(
        request,
        "sales/client_orders_report.html",
        {"orders": orders},
    )
