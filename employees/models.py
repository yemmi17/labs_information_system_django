from django.db import models
from django.urls import reverse


class Employee(models.Model):
    last_name = models.CharField("Фамилия", max_length=100)
    first_name = models.CharField("Имя", max_length=100)
    middle_name = models.CharField("Отчество", max_length=100, blank=True)
    position = models.CharField("Должность", max_length=150)
    address = models.CharField("Адрес", max_length=255)
    work_phone = models.CharField("Рабочий телефон", max_length=50)
    personal_phone = models.CharField("Личный телефон", max_length=50)

    class Meta:
        ordering = ("last_name", "first_name", "middle_name")
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()

    def get_absolute_url(self):
        return reverse("employee_list")
