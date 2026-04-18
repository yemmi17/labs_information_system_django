from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EmployeeForm
from .models import Employee


def home(request):
    return render(request, "employees/home.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("employee_list")

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("employee_list")

    return render(request, "registration/login.html", {"form": form})


def employee_list(request):
    context = {
        "employees": Employee.objects.all(),
        "is_guest": not request.user.is_authenticated,
        "can_add": can_add_employee(request.user),
        "can_edit": can_edit_employee(request.user),
        "can_delete": can_delete_employee(request.user),
    }
    return render(request, "employees/employee_list.html", context)


@login_required
def employee_create(request):
    if not can_add_employee(request.user):
        return HttpResponseForbidden("У вас нет прав на добавление сотрудников.")

    form = EmployeeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Сотрудник успешно добавлен.")
        return redirect("employee_list")

    return render(request, "employees/employee_form.html", {"form": form, "title": "Добавить сотрудника"})


@login_required
def employee_update(request, pk):
    if not can_edit_employee(request.user):
        return HttpResponseForbidden("У вас нет прав на редактирование сотрудников.")

    employee = get_object_or_404(Employee, pk=pk)
    form = EmployeeForm(request.POST or None, instance=employee)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Данные сотрудника обновлены.")
        return redirect("employee_list")

    return render(
        request,
        "employees/employee_form.html",
        {"form": form, "title": "Редактировать сотрудника", "employee": employee},
    )


@login_required
def employee_delete(request, pk):
    if not can_delete_employee(request.user):
        return HttpResponseForbidden("У вас нет прав на удаление сотрудников.")

    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        employee.delete()
        messages.success(request, "Сотрудник удалён.")
        return redirect("employee_list")

    return render(request, "employees/employee_confirm_delete.html", {"employee": employee})


def can_add_employee(user):
    return user.is_authenticated and user.groups.filter(name="director").exists()


def can_edit_employee(user):
    return user.is_authenticated and user.groups.filter(name__in=["director", "deputy"]).exists()


def can_delete_employee(user):
    return user.is_authenticated and user.groups.filter(name="director").exists()
