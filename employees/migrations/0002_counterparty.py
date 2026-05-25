from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Counterparty",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, verbose_name="Наименование")),
                ("inn", models.CharField(max_length=12, verbose_name="ИНН")),
                ("code", models.CharField(max_length=20, unique=True, verbose_name="Код")),
                ("marked_for_deletion", models.BooleanField(default=False, verbose_name="Помечен на удаление")),
                ("duplicate_note", models.CharField(blank=True, max_length=255, verbose_name="Комментарий проверки")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создан")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Изменен")),
            ],
            options={
                "verbose_name": "Контрагент",
                "verbose_name_plural": "Контрагенты",
                "ordering": ("name", "code"),
            },
        ),
    ]
