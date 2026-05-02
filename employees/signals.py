# -*- coding: utf-8 -*-
# ===== Служебный комментарий модуля ==========================================
# Модуль: employees.signals
# Назначение: автоматическая настройка ролей, прав и демонстрационных данных.
# Исполнитель изменения: Yemmi
# Дата изменения: 02.05.2026
# Причина изменения: подробно описать специфические операции с БД и правами.
# Первоначальный фрагмент: receiver post_migrate с созданием групп и demo users.
# =============================================================================

from django.contrib.auth.models import Group, Permission, User
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Employee


@receiver(post_migrate)
def setup_roles(sender, **kwargs):
    """Обрабатывает сигнал post_migrate для настройки ролей и демо-данных.

    Тип подпрограммы: обработчик сигнала Django.
    Формальные параметры: sender - приложение, вызвавшее post_migrate; kwargs - служебные данные сигнала.
    Фактические данные: таблицы auth_group, auth_permission, auth_user и employees_employee.
    Условия: выполняется только после миграции приложения employees.
    Возвращает: None.
    """
    # Сигнал post_migrate приходит от каждого приложения, поэтому фильтруем только employees.
    if sender.name != "employees":
        return

    # Загружаем все права доступа для приложения employees и упаковываем их в словарь.
    permissions = Permission.objects.filter(content_type__app_label="employees")
    # Словарь ускоряет обращение к правам по codename и делает назначения ролей явными.
    permission_map = {permission.codename: permission for permission in permissions}

    # Группа director получает полный набор прав на сотрудников.
    director_group, _ = Group.objects.get_or_create(name="director")
    # Группа deputy получает право просмотра и редактирования.
    deputy_group, _ = Group.objects.get_or_create(name="deputy")
    # Группа secretary получает только право просмотра.
    secretary_group, _ = Group.objects.get_or_create(name="secretary")

    # Назначаем директору все CRUD-права на модель Employee.
    director_group.permissions.set(
        [
            permission_map["add_employee"],
            permission_map["change_employee"],
            permission_map["delete_employee"],
            permission_map["view_employee"],
        ]
    )
    # Назначаем заместителю права изменения и просмотра без создания и удаления.
    deputy_group.permissions.set([permission_map["change_employee"], permission_map["view_employee"]])
    # Назначаем секретарю только право просмотра.
    secretary_group.permissions.set([permission_map["view_employee"]])

    # Создаем демонстрационных пользователей для удобного тестирования прав.
    create_demo_user("director", "director123", director_group, "Иван", "Иванов")
    create_demo_user("deputy", "deputy123", deputy_group, "Пётр", "Петров")
    create_demo_user("secretary", "secretary123", secretary_group, "Анна", "Сидорова")

    # Демонстрационные сотрудники создаются только в пустой таблице, чтобы не дублировать данные.
    if not Employee.objects.exists():
        # bulk_create выполняет одну групповую вставку и экономит обращения к базе данных.
        Employee.objects.bulk_create(
            [
                # Первая демонстрационная запись показывает роль директора.
                Employee(
                    last_name="Иванов",
                    first_name="Иван",
                    middle_name="Сергеевич",
                    position="Директор",
                    address="г. Москва, ул. Центральная, д. 10",
                    work_phone="+7 (495) 100-10-10",
                    personal_phone="+7 (999) 111-11-11",
                ),
                # Вторая демонстрационная запись показывает роль секретаря.
                Employee(
                    last_name="Петрова",
                    first_name="Мария",
                    middle_name="Алексеевна",
                    position="Секретарь",
                    address="г. Москва, ул. Парковая, д. 5",
                    work_phone="+7 (495) 200-20-20",
                    personal_phone="+7 (999) 222-22-22",
                ),
                # Третья демонстрационная запись показывает обычного сотрудника.
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

    Тип подпрограммы: вспомогательная функция работы с БД.
    Формальные параметры:
    username - строковый логин пользователя;
    password - строковый пароль демонстрационной учетной записи;
    group - объект Group, назначаемый пользователю;
    first_name - имя пользователя;
    last_name - фамилия пользователя.
    Фактические данные: таблицы auth_user и auth_user_groups.
    Условия: group должен существовать до вызова функции.
    Возвращает: None.
    """
    # get_or_create предотвращает повторное создание пользователя при каждом migrate.
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"first_name": first_name, "last_name": last_name},
    )
    # Пароль задается только новой учетной записи, чтобы не сбрасывать его при повторных миграциях.
    if created:
        user.set_password(password)
        user.save()
    # Добавляем пользователя в группу, если связь еще не создана.
    if not user.groups.filter(pk=group.pk).exists():
        user.groups.add(group)
