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

from .models import Counterparty, Employee


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


class CounterpartyInnTests(TestCase):
    """Проверки лабораторной №7: валидация ИНН и пометка дублей."""

    def test_invalid_inn_is_rejected_by_form(self):
        response = self.client.post(
            reverse("counterparty_create"),
            {"name": "ООО Ромашка", "code": "C-001", "inn": "abc"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ИНН должен содержать 10 или 12 цифр.")

    def test_duplicate_inn_can_be_marked_for_deletion(self):
        Counterparty.objects.create(name="ООО Альфа", code="C-001", inn="7701234567")
        duplicate = Counterparty.objects.create(name="ООО Альфа дубль", code="C-002", inn="7701234567")

        response = self.client.get(reverse("counterparty_mark_duplicates"))

        duplicate.refresh_from_db()
        self.assertRedirects(response, reverse("counterparty_list"))
        self.assertTrue(duplicate.marked_for_deletion)
        self.assertIn("Дубликат ИНН", duplicate.duplicate_note)
