# -*- coding: cp1251 -*-
"""
================================================================================
employees.signals
--------------------------------------------------------------------------------
Модуль определяет обработчики сигналов Django, автоматически создающие
группы ролей, права доступа и демонстрационных пользователей после миграции.

Изменение выполнено: GitHub Copilot, 18.04.2026
Причина: добавить работу с комментариями и объяснить автоматическую настройку ролей.
================================================================================
"""

from django.contrib.auth.models import Group, Permission, User
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Employee


@receiver(post_migrate)
def setup_roles(sender, **kwargs):
    """Обрабатывает сигнал post_migrate для настройки ролей и демо-данных.

    sender: объект приложения, вызвавшего сигнал. Функция выполняется только
    когда приложение employees завершило миграцию, чтобы исключить повторные
    действия для других приложений.
    """
    if sender.name != "employees":
        return

    # Загружаем все права доступа для приложения employees и упаковываем их в словарь.
    permissions = Permission.objects.filter(content_type__app_label="employees")
    permission_map = {permission.codename: permission for permission in permissions}

    director_group, _ = Group.objects.get_or_create(name="director")
    deputy_group, _ = Group.objects.get_or_create(name="deputy")
    secretary_group, _ = Group.objects.get_or_create(name="secretary")

    director_group.permissions.set(
        [
            permission_map["add_employee"],
            permission_map["change_employee"],
            permission_map["delete_employee"],
            permission_map["view_employee"],
        ]
    )
    deputy_group.permissions.set([permission_map["change_employee"], permission_map["view_employee"]])
    secretary_group.permissions.set([permission_map["view_employee"]])

    # Создаем демонстрационных пользователей для удобного тестирования прав.
    create_demo_user("director", "director123", director_group, "Иван", "Иванов")
    create_demo_user("deputy", "deputy123", deputy_group, "Пётр", "Петров")
    create_demo_user("secretary", "secretary123", secretary_group, "Анна", "Сидорова")

    if not Employee.objects.exists():
        Employee.objects.bulk_create(
            [
                Employee(
                    last_name="Иванов",
                    first_name="Иван",
                    middle_name="Сергеевич",
                    position="Директор",
                    address="г. Москва, ул. Центральная, д. 10",
                    work_phone="+7 (495) 100-10-10",
                    personal_phone="+7 (999) 111-11-11",
                ),
                Employee(
                    last_name="Петрова",
                    first_name="Мария",
                    middle_name="Алексеевна",
                    position="Секретарь",
                    address="г. Москва, ул. Парковая, д. 5",
                    work_phone="+7 (495) 200-20-20",
                    personal_phone="+7 (999) 222-22-22",
                ),
                Employee(
                    last_name="Смирнов",
                    first_name="Олег",
                    middle_name="Игоревич",
                    position="Инженер",
                    address="г. Москва, пр-т Мира, д. 42",
                    work_phone="+7 (495) 300-30-30",
                    personal_phone="+7 (999) 333-33-33",
                ),
            ]
        )


def create_demo_user(username, password, group, first_name, last_name):
    """Создает пользователя и добавляет его в указанную группу.

    username: имя пользователя для входа.
    password: пароль учетной записи.
    group: объект Group для назначения разрешений.
    first_name: имя сотрудника.
    last_name: фамилия сотрудника.
    """
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"first_name": first_name, "last_name": last_name},
    )
    if created:
        user.set_password(password)
        user.save()
    if not user.groups.filter(pk=group.pk).exists():
        user.groups.add(group)
