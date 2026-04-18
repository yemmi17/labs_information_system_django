from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Employee


class EmployeeAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
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
        self.client = Client()

    def test_guest_sees_only_public_fields(self):
        response = self.client.get(reverse("employee_list"))

        self.assertContains(response, "Тестов")
        self.assertContains(response, "Аналитик")
        self.assertContains(response, "+7 (495) 400-40-40")
        self.assertNotContains(response, "ул. Тестовая")
        self.assertNotContains(response, "+7 (999) 444-44-44")

    def test_secretary_cannot_open_create_page(self):
        user = self._create_user("sec-test", "secretary")
        self.client.force_login(user)

        response = self.client.get(reverse("employee_create"))

        self.assertEqual(response.status_code, 403)

    def test_deputy_can_edit_but_cannot_delete(self):
        user = self._create_user("dep-test", "deputy")
        self.client.force_login(user)

        edit_response = self.client.get(reverse("employee_update", args=[self.employee.pk]))
        delete_response = self.client.get(reverse("employee_delete", args=[self.employee.pk]))

        self.assertEqual(edit_response.status_code, 200)
        self.assertEqual(delete_response.status_code, 403)

    def test_director_can_open_all_management_pages(self):
        user = self._create_user("dir-test", "director")
        self.client.force_login(user)

        create_response = self.client.get(reverse("employee_create"))
        edit_response = self.client.get(reverse("employee_update", args=[self.employee.pk]))
        delete_response = self.client.get(reverse("employee_delete", args=[self.employee.pk]))

        self.assertEqual(create_response.status_code, 200)
        self.assertEqual(edit_response.status_code, 200)
        self.assertEqual(delete_response.status_code, 200)

    def _create_user(self, username, group_name):
        user = User.objects.create_user(username=username, password="pass12345")
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
        return user

# Create your tests here.
