from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Material",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=20, unique=True, verbose_name="Код")),
                ("name", models.CharField(max_length=200, verbose_name="Наименование")),
                ("accounting_account", models.CharField(max_length=20, verbose_name="Счет учета")),
                ("quantity", models.PositiveIntegerField(default=0, verbose_name="Количество")),
            ],
            options={
                "verbose_name": "Материал",
                "verbose_name_plural": "Материалы",
                "ordering": ("code",),
            },
        ),
    ]
