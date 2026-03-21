from decimal import Decimal
import base64
from io import BytesIO

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

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


def _fig_to_base64():
    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format="png", dpi=120)
    plt.close()
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def _build_line_chart(values, title, mean_line=False):
    fig, ax = plt.subplots(figsize=(8, 3.2))
    x = np.arange(1, len(values) + 1)
    ax.plot(x, values, marker="o", color="#1464b4", linewidth=2)
    if mean_line and values:
        mean_value = float(np.mean(values))
        ax.axhline(mean_value, color="red", linestyle="--", linewidth=1.5)
    ax.set_title(title)
    ax.set_xlabel("Номер точки")
    ax.set_ylabel("Значение")
    ax.grid(alpha=0.3)
    return _fig_to_base64()


def _build_bar_chart(values, title):
    fig, ax = plt.subplots(figsize=(8, 3.2))
    x = np.arange(1, len(values) + 1)
    ax.bar(x, values, color="#2f9a55")
    ax.set_title(title)
    ax.set_xlabel("Номер точки")
    ax.set_ylabel("Значение")
    ax.grid(axis="y", alpha=0.3)
    return _fig_to_base64()


def parameter_monitor_view(request):
    history_key = "monitor_values_history"
    previous_values = request.session.get(history_key, [])
    previous_values = previous_values[-10:]

    context = {
        "current_value": None,
        "previous_values": previous_values,
        "all_values": previous_values,
        "selected_values": [],
        "history_size": min(5, max(2, len(previous_values) or 5)),
        "percent_threshold": 20,
        "allowed_min": 0,
        "allowed_max": 100,
        "selection_type": "gt",
        "boundary_value": 50,
        "multiple_value": 2,
        "warning_triggered": False,
        "alarm_triggered": False,
        "warning_message": "",
        "alarm_message": "",
        "chart_all": "",
        "chart_selected": "",
        "chart_bar": "",
        "selected_mean": None,
    }

    if request.method == "POST":
        def _to_float(name, default):
            try:
                return float(request.POST.get(name, default))
            except (TypeError, ValueError):
                return float(default)

        def _to_int(name, default):
            try:
                return int(request.POST.get(name, default))
            except (TypeError, ValueError):
                return int(default)

        current_value = _to_float("current_value", 0)
        history_size = _to_int("history_size", 5)
        history_size = min(10, max(2, history_size))

        percent_threshold = _to_float("percent_threshold", 20)
        percent_threshold = min(40, max(5, percent_threshold))

        allowed_min = _to_float("allowed_min", 0)
        allowed_max = _to_float("allowed_max", 100)
        if allowed_min > allowed_max:
            allowed_min, allowed_max = allowed_max, allowed_min

        selection_type = request.POST.get("selection_type", "gt")
        boundary_value = _to_float("boundary_value", 50)
        multiple_value = _to_int("multiple_value", 2)
        multiple_value = max(1, multiple_value)

        values = (previous_values + [current_value])[-history_size:]
        selected_values = []

        if selection_type == "gt":
            selected_values = [v for v in values if v > boundary_value]
        elif selection_type == "lt":
            selected_values = [v for v in values if v < boundary_value]
        elif selection_type == "multiple":
            selected_values = [v for v in values if int(v) % multiple_value == 0]

        warning_triggered = False
        warning_message = ""
        if previous_values:
            prev = previous_values[-1]
            base = abs(prev) if prev != 0 else 1
            change_percent = abs(current_value - prev) / base * 100
            if change_percent > percent_threshold:
                warning_triggered = True
                warning_message = (
                    f"Предупреждение: изменение текущего значения составило "
                    f"{change_percent:.2f}% (порог {percent_threshold:.2f}%)."
                )

        alarm_triggered = current_value < allowed_min or current_value > allowed_max
        alarm_message = ""
        if alarm_triggered:
            alarm_message = (
                f"Тревога: значение {current_value:.2f} вне диапазона "
                f"[{allowed_min:.2f}; {allowed_max:.2f}]."
            )

        chart_all = _build_line_chart(values, "Текущие и предыдущие значения")
        chart_selected = ""
        chart_bar = ""
        selected_mean = None
        if selected_values:
            selected_mean = float(np.mean(selected_values))
            chart_selected = _build_line_chart(
                selected_values,
                "Выборочные значения (красная линия - среднее)",
                mean_line=True,
            )
            chart_bar = _build_bar_chart(selected_values, "Диаграмма выборочных значений")

        request.session[history_key] = (previous_values + [current_value])[-10:]

        context.update(
            {
                "current_value": current_value,
                "previous_values": previous_values[-history_size:],
                "all_values": values,
                "selected_values": selected_values,
                "history_size": history_size,
                "percent_threshold": percent_threshold,
                "allowed_min": allowed_min,
                "allowed_max": allowed_max,
                "selection_type": selection_type,
                "boundary_value": boundary_value,
                "multiple_value": multiple_value,
                "warning_triggered": warning_triggered,
                "alarm_triggered": alarm_triggered,
                "warning_message": warning_message,
                "alarm_message": alarm_message,
                "chart_all": chart_all,
                "chart_selected": chart_selected,
                "chart_bar": chart_bar,
                "selected_mean": selected_mean,
            }
        )

    return render(request, "sales/parameter_monitor.html", context)
