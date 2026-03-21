from django.urls import path

from . import views

app_name = "sales"

urlpatterns = [
    path("monitor/", views.parameter_monitor_view, name="parameter_monitor"),
    path("clients/search/", views.client_search_view, name="client_search"),
    path("products/", views.product_list_view, name="product_list"),
    path("orders/new/", views.order_create_view, name="order_create"),
    path("orders/<int:pk>/", views.order_detail_view, name="order_detail"),
    path(
        "reports/client-orders/",
        views.client_orders_report_view,
        name="client_orders_report",
    ),
]

