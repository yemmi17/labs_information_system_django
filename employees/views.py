# -*- coding: utf-8 -*-
# ===== Служебный комментарий модуля ==========================================
# Модуль: employees.views
# Назначение: обработка HTTP-запросов интерфейса справочника сотрудников.
# Исполнитель изменения: Yemmi
# Дата изменения: 02.05.2026
# Причина изменения: добавить подробные комментарии к операциям CRUD и доступам.
# Первоначальный фрагмент: Django views с краткими docstring.
# =============================================================================

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import models
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CounterpartyForm, EmployeeForm
from .models import Counterparty, Employee


def home(request):
    """Отображает стартовую страницу приложения.

    Тип подпрограммы: функция-представление Django.
    Формальные параметры: request - HTTP-запрос Django.
    Фактические данные: объект запроса передается Django URL-диспетчером.
    Условия: шаблон employees/home.html должен существовать.
    Возвращает: HttpResponse со стартовой HTML-страницей.
    """
    # Рендерим главную страницу без дополнительного контекста.
    return render(request, "employees/home.html")


def login_view(request):
    """Обрабатывает форму авторизации и редиректит на список сотрудников.

    Тип подпрограммы: функция-представление Django.
    Формальные параметры: request - HTTP-запрос Django.
    Фактические данные: request.POST содержит логин и пароль при POST-запросе.
    Условия: AuthenticationForm должна пройти валидацию для входа пользователя.
    Возвращает: HttpResponse со страницей входа или HttpResponseRedirect.
    """
    # Уже авторизованному пользователю форма входа не нужна.
    if request.user.is_authenticated:
        return redirect("employee_list")

    # Для GET создается пустая форма, для POST форма получает отправленные данные.
    form = AuthenticationForm(request, data=request.POST or None)
    # При корректной POST-форме создаем пользовательскую сессию.
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("employee_list")

    # Если это GET или форма невалидна, показываем страницу входа с ошибками формы.
    return render(request, "registration/login.html", {"form": form})


def employee_list(request):
    """Формирует контекст и отображает список сотрудников.

    Тип подпрограммы: функция-представление Django.
    Формальные параметры: request - HTTP-запрос Django.
    Фактические данные: request.user определяет роль и доступные действия.
    Условия: модель Employee и шаблон employee_list.html доступны приложению.
    Возвращает: HttpResponse со списком сотрудников.
    """
    # Контекст явно содержит данные таблицы и флаги разрешений для шаблона.
    context = {
        # QuerySet всех сотрудников; порядок задан в Employee.Meta.ordering.
        "employees": Employee.objects.all(),
        # Гость видит только публичную часть карточки сотрудника.
        "is_guest": not request.user.is_authenticated,
        # Флаг отображения действия создания сотрудника.
        "can_add": can_add_employee(request.user),
        # Флаг отображения действия редактирования сотрудника.
        "can_edit": can_edit_employee(request.user),
        # Флаг отображения действия удаления сотрудника.
        "can_delete": can_delete_employee(request.user),
    }
    # Передаем контекст в HTML-шаблон списка сотрудников.
    return render(request, "employees/employee_list.html", context)


@login_required
def employee_create(request):
    """Создает новую запись сотрудника через форму и сохраняет в базу данных.

    Тип подпрограммы: защищенная функция-представление Django.
    Формальные параметры: request - HTTP-запрос Django.
    Фактические данные: request.POST содержит поля EmployeeForm при POST-запросе.
    Условия: пользователь должен быть авторизован и состоять в группе director.
    Возвращает: страницу формы, запрет доступа или перенаправление после сохранения.
    """
    # Защищаем операцию создания на сервере, а не только скрываем кнопку в интерфейсе.
    if not can_add_employee(request.user):
        return HttpResponseForbidden("У вас нет прав на добавление сотрудников.")

    # На GET форма пустая; на POST форма заполняется присланными данными.
    form = EmployeeForm(request.POST or None)
    # Сохраняем сотрудника только после проверки метода и валидности формы.
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Сотрудник успешно добавлен.")
        return redirect("employee_list")

    # Показываем форму создания при GET или при ошибках валидации.
    return render(request, "employees/employee_form.html", {"form": form, "title": "Добавить сотрудника"})


@login_required
def employee_update(request, pk):
    """Редактирует существующего сотрудника, выбранного по первичному ключу pk.

    Тип подпрограммы: защищенная функция-представление Django.
    Формальные параметры: request - HTTP-запрос Django; pk - первичный ключ Employee.
    Фактические данные: request.POST содержит новые значения полей при POST-запросе.
    Условия: пользователь должен состоять в группе director или deputy.
    Возвращает: страницу формы, запрет доступа, 404 или перенаправление после сохранения.
    """
    # Проверяем право редактирования до чтения и изменения объекта.
    if not can_edit_employee(request.user):
        return HttpResponseForbidden("У вас нет прав на редактирование сотрудников.")

    # Получаем сотрудника по pk или возвращаем 404, если запись отсутствует.
    employee = get_object_or_404(Employee, pk=pk)
    # Привязываем форму к найденному объекту, чтобы save() обновлял запись, а не создавал новую.
    form = EmployeeForm(request.POST or None, instance=employee)
    # При валидной POST-форме сохраняем изменения и возвращаем пользователя к списку.
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Данные сотрудника обновлены.")
        return redirect("employee_list")

    # На GET или ошибках валидации показываем форму с текущими значениями сотрудника.
    return render(
        request,
        "employees/employee_form.html",
        {"form": form, "title": "Редактировать сотрудника", "employee": employee},
    )


@login_required
def employee_delete(request, pk):
    """Удаляет сотрудника после подтверждения на странице удаления.

    Тип подпрограммы: защищенная функция-представление Django.
    Формальные параметры: request - HTTP-запрос Django; pk - первичный ключ Employee.
    Фактические данные: POST-запрос подтверждает намерение удалить запись.
    Условия: пользователь должен состоять в группе director.
    Возвращает: страницу подтверждения, запрет доступа, 404 или редирект после удаления.
    """
    # Удаление разрешено только директору, поэтому проверяем роль на сервере.
    if not can_delete_employee(request.user):
        return HttpResponseForbidden("У вас нет прав на удаление сотрудников.")

    # Получаем удаляемого сотрудника или возвращаем 404 при неверном pk.
    employee = get_object_or_404(Employee, pk=pk)
    # Фактическое удаление выполняется только POST-запросом после подтверждения формы.
    if request.method == "POST":
        employee.delete()
        messages.success(request, "Сотрудник удалён.")
        return redirect("employee_list")

    # Для GET показываем страницу подтверждения удаления.
    return render(request, "employees/employee_confirm_delete.html", {"employee": employee})


def counterparty_list(request):
    """Отображает справочник контрагентов и результаты проверки ИНН."""
    duplicate_groups = find_duplicate_inn_groups()
    context = {
        "counterparties": Counterparty.objects.all(),
        "duplicate_groups": duplicate_groups,
    }
    return render(request, "employees/counterparty_list.html", context)


def counterparty_create(request):
    """Создает новую карточку контрагента."""
    form = CounterpartyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Контрагент добавлен.")
        return redirect("counterparty_list")
    return render(request, "employees/counterparty_form.html", {"form": form, "title": "Добавить контрагента"})


def counterparty_update(request, pk):
    """Редактирует карточку контрагента."""
    counterparty = get_object_or_404(Counterparty, pk=pk)
    form = CounterpartyForm(request.POST or None, instance=counterparty)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Контрагент обновлен.")
        return redirect("counterparty_list")
    return render(
        request,
        "employees/counterparty_form.html",
        {"form": form, "title": "Редактировать контрагента", "counterparty": counterparty},
    )


def counterparty_check_inn(request, pk):
    """Проверяет выбранный ИНН на совпадения и подстрочные вхождения."""
    counterparty = get_object_or_404(Counterparty, pk=pk)
    candidates = Counterparty.objects.exclude(pk=counterparty.pk)
    matches = [
        item
        for item in candidates
        if item.inn == counterparty.inn or item.inn in counterparty.inn or counterparty.inn in item.inn
    ]

    if not counterparty.is_inn_valid:
        messages.error(request, f"У контрагента {counterparty.name} некорректный ИНН.")
    elif matches:
        names = ", ".join(f"{item.name} [{item.code}]" for item in matches)
        messages.warning(request, f"Найдены совпадения ИНН для {counterparty.name}: {names}.")
    else:
        messages.success(request, f"ИНН {counterparty.inn} для {counterparty.name} уникален.")

    return redirect("counterparty_list")


def counterparty_mark_duplicates(request):
    """Помечает дублирующиеся ИНН на удаление, оставляя первую запись активной."""
    marked_count = 0
    for group in find_duplicate_inn_groups():
        duplicates = list(Counterparty.objects.filter(inn=group["inn"]).order_by("pk"))
        for duplicate in duplicates[1:]:
            duplicate.marked_for_deletion = True
            duplicate.duplicate_note = f"Дубликат ИНН {group['inn']}; основной код {duplicates[0].code}"
            duplicate.save(update_fields=["marked_for_deletion", "duplicate_note", "updated_at"])
            marked_count += 1

    if marked_count:
        messages.warning(request, f"Помечено на удаление дублей: {marked_count}.")
    else:
        messages.success(request, "Дубли ИНН не найдены.")
    return redirect("counterparty_list")


def find_duplicate_inn_groups():
    """Возвращает группы ИНН, встречающиеся более одного раза."""
    duplicates = (
        Counterparty.objects.values("inn")
        .order_by("inn")
        .annotate(count=models.Count("id"))
        .filter(count__gt=1)
    )
    return list(duplicates)


# ===== Функции проверки прав доступа =====

def can_add_employee(user):
    """Возвращает True, если пользователь может добавлять сотрудников.

    Тип подпрограммы: функция проверки прав.
    Формальные параметры: user - объект пользователя Django.
    Фактические данные: user.is_authenticated и членство в группе director.
    Условия: у анонимного пользователя groups не должен вычисляться как разрешение.
    Возвращает: bool.
    """
    # Добавление доступно только авторизованному директору.
    return user.is_authenticated and user.groups.filter(name="director").exists()


def can_edit_employee(user):
    """Возвращает True, если пользователь может редактировать сотрудников.

    Тип подпрограммы: функция проверки прав.
    Формальные параметры: user - объект пользователя Django.
    Фактические данные: членство пользователя в группах director или deputy.
    Условия: пользователь должен быть авторизован.
    Возвращает: bool.
    """
    # Редактирование разрешено директору и заместителю директора.
    return user.is_authenticated and user.groups.filter(name__in=["director", "deputy"]).exists()


def can_delete_employee(user):
    """Возвращает True, если пользователь может удалять сотрудников.

    Тип подпрограммы: функция проверки прав.
    Формальные параметры: user - объект пользователя Django.
    Фактические данные: членство пользователя в группе director.
    Условия: пользователь должен быть авторизован.
    Возвращает: bool.
    """
    # Удаление является наиболее опасной CRUD-операцией и доступно только директору.
    return user.is_authenticated and user.groups.filter(name="director").exists()
