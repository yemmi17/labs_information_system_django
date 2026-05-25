from django.urls import path

from . import views


app_name = "case_builder"

urlpatterns = [
    path("", views.designer, name="designer"),
]
