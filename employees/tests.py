# -*- coding: utf-8 -*-
# ===== Служебный комментарий модуля ==========================================
# Модуль: employees.tests
# Назначение: автоматическая проверка правил доступа к справочнику сотрудников.
# Исполнитель изменения: Yemmi
# Дата изменения: 02.05.2026
# Причина изменения: добавить комментарии к тестовым данным и проверкам.
# Первоначальный фрагмент: TestCase с проверками ролей director/deputy/secretary.
# =============================================================================

from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import WaybillForm
from .models import Car, Driver, DriverCar, Employee, Waybill


class EmployeeAccessTests(TestCase):
    """Набор тестов для проверки доступа к страницам управления сотрудниками.

    Тип: класс Django TestCase.
    Формальные данные: методы test_* запускаются тестовым раннером Django.
    Фактические данные: тестовая база, тестовый HTTP-клиент и группы ролей.
    Условия: миграции и сигнал setup_roles создают группы пользователей.
    Результат: подтверждение ожидаемых HTTP-статусов и видимости полей.
    """

    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные, которые используются во всех тестах класса.

        Тип подпрограммы: classmethod подготовки фикстур.
        Формальные параметры: cls - класс теста.
        Фактические данные: одна запись Employee в тестовой базе.
        Условия: тестовая база уже создана Django.
        Возвращает: None.
        """
        # Создаем сотрудника один раз для всех тестов класса.
        cls.employee = Employee.objects.create(
            last_name="Тестов",
            first_name="Тест",
            middle_name="Тестович",
            position="Аналитик",
            address="г. Москва, ул. Тестовая, д. 1",
            work_phone="+7 (495) 400-40-40",
            personal_phone="+7 (999) 444-44-44",
        )

    def setUp(self):
        """Настраивает HTTP-клиент для каждого отдельного теста.

        Тип подпрограммы: метод подготовки теста.
        Формальные параметры: self - экземпляр тестового класса.
        Фактические данные: django.test.Client.
        Условия: вызывается перед каждым методом test_*.
        Возвращает: None.
        """
        # Новый клиент изолирует состояние запросов между тестами.
        self.client = Client()

    def test_guest_sees_only_public_fields(self):
        """Гость видит только публичные поля сотрудника и не видит закрытую информацию."""
        # Гость открывает список сотрудников без аутентификации.
        response = self.client.get(reverse("employee_list"))

        # Публичные поля должны отображаться.
        self.assertContains(response, "Тестов")
        self.assertContains(response, "Аналитик")
        self.assertContains(response, "+7 (495) 400-40-40")
        # Закрытые поля не должны отображаться гостю.
        self.assertNotContains(response, "ул. Тестовая")
        self.assertNotContains(response, "+7 (999) 444-44-44")

    def test_secretary_cannot_open_create_page(self):
        """Секретарь не имеет права открывать страницу создания сотрудника."""
        # Создаем пользователя с ролью secretary и авторизуем его в тестовом клиенте.
        user = self._create_user("sec-test", "secretary")
        self.client.force_login(user)

        # Проверяем серверный запрет доступа к созданию сотрудника.
        response = self.client.get(reverse("employee_create"))

        self.assertEqual(response.status_code, 403)

    def test_deputy_can_edit_but_cannot_delete(self):
        """Заместитель имеет право редактирования, но не удаления сотрудников."""
        # Создаем пользователя с ролью deputy и авторизуем его.
        user = self._create_user("dep-test", "deputy")
        self.client.force_login(user)

        # Заместитель открывает страницу редактирования существующего сотрудника.
        edit_response = self.client.get(reverse("employee_update", args=[self.employee.pk]))
        # Заместитель пытается открыть страницу удаления того же сотрудника.
        delete_response = self.client.get(reverse("employee_delete", args=[self.employee.pk]))

        # Редактирование разрешено, удаление запрещено.
        self.assertEqual(edit_response.status_code, 200)
        self.assertEqual(delete_response.status_code, 403)

    def test_director_can_open_all_management_pages(self):
        """Директор может открыть все страницы управления сотрудниками."""
        # Создаем пользователя с ролью director и авторизуем его.
        user = self._create_user("dir-test", "director")
        self.client.force_login(user)

        # Директор проверяет страницу создания.
        create_response = self.client.get(reverse("employee_create"))
        # Директор проверяет страницу редактирования.
        edit_response = self.client.get(reverse("employee_update", args=[self.employee.pk]))
        # Директор проверяет страницу удаления.
        delete_response = self.client.get(reverse("employee_delete", args=[self.employee.pk]))

        # Все управленческие страницы должны быть доступны директору.
        self.assertEqual(create_response.status_code, 200)
        self.assertEqual(edit_response.status_code, 200)
        self.assertEqual(delete_response.status_code, 200)

    def _create_user(self, username, group_name):
        """Создает пользователя и добавляет его в указанную группу ролевых прав.

        Тип подпрограммы: вспомогательный метод теста.
        Формальные параметры: username - логин; group_name - имя группы Django.
        Фактические данные: таблицы auth_user, auth_group и m2m-связь user.groups.
        Условия: группа group_name должна быть создана сигналом post_migrate.
        Возвращает: объект User.
        """
        # Создаем пользователя с тестовым паролем.
        user = User.objects.create_user(username=username, password="pass12345")
        # Получаем существующую группу по имени роли.
        group = Group.objects.get(name=group_name)
        # Назначаем пользователю роль через m2m-связь.
        user.groups.add(group)
        # Возвращаем пользователя вызывающему тесту для авторизации.
        return user


class TransportAccountingTests(TestCase):
    """Проверки лабораторной №9: пробег, расход топлива и ограничения формы."""

    @classmethod
    def setUpTestData(cls):
        cls.employee = Employee.objects.create(
            last_name="Иванов",
            first_name="Иван",
            position="Водитель",
            address="Москва",
            work_phone="+7",
            personal_phone="+7",
        )
        cls.driver = Driver.objects.create(employee=cls.employee)
        cls.car = Car.objects.create(
            brand="ГАЗ",
            plate_number="А001АА",
            production_year=2020,
            fuel_rate_per_km="0.120",
        )
        DriverCar.objects.create(driver=cls.driver, car=cls.car)

    def test_waybill_calculates_distance_and_fuel_consumption(self):
        waybill = Waybill.objects.create(
            driver=self.driver,
            car=self.car,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timezone.timedelta(hours=2),
            start_mileage=1000,
            end_mileage=1150,
        )

        self.assertEqual(waybill.distance, 150)
        self.assertEqual(str(waybill.fuel_consumption), "18.000")

    def test_waybill_form_rejects_unassigned_car(self):
        other_car = Car.objects.create(
            brand="УАЗ",
            plate_number="В002ВВ",
            production_year=2021,
            fuel_rate_per_km="0.150",
        )
        form = WaybillForm(
            data={
                "driver": self.driver.pk,
                "car": other_car.pk,
                "departure_time": "2026-05-25T10:00",
                "arrival_time": "2026-05-25T12:00",
                "start_mileage": 10,
                "end_mileage": 20,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("car", form.errors)

    def test_transport_dashboard_renders_stats(self):
        Waybill.objects.create(
            driver=self.driver,
            car=self.car,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timezone.timedelta(hours=1),
            start_mileage=0,
            end_mileage=50,
        )

        response = self.client.get(reverse("transport_dashboard"))

        self.assertContains(response, "Учет пробега автотранспорта")
        self.assertContains(response, "50 км")
