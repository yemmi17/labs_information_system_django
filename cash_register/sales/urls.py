from django.urls import path

from . import views

urlpatterns = [
    path("", views.profit_by_group, name="profit_by_group"),
    path("sales/", views.sale_list, name="sale_list"),
]
