from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Car",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("brand", models.CharField(max_length=100, verbose_name="Марка автомобиля")),
                ("plate_number", models.CharField(max_length=20, unique=True, verbose_name="Гос. номер")),
                ("production_year", models.PositiveIntegerField(verbose_name="Год выпуска")),
                ("fuel_rate_per_km", models.DecimalField(decimal_places=3, max_digits=6, verbose_name="Норма расхода литров на 1 км")),
            ],
            options={
                "verbose_name": "Автомобиль",
                "verbose_name_plural": "Автомобили",
                "ordering": ("plate_number",),
            },
        ),
        migrations.CreateModel(
            name="Driver",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("employee", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="employees.employee", verbose_name="Сотрудник")),
            ],
            options={
                "verbose_name": "Водитель",
                "verbose_name_plural": "Водители",
                "ordering": ("employee__last_name", "employee__first_name"),
            },
        ),
        migrations.CreateModel(
            name="DriverCar",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("car", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="employees.car", verbose_name="Автомобиль")),
                ("driver", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="employees.driver", verbose_name="Водитель")),
            ],
            options={
                "verbose_name": "Автомобиль водителя",
                "verbose_name_plural": "Автомобили водителей",
                "unique_together": {("driver", "car")},
            },
        ),
        migrations.AddField(
            model_name="driver",
            name="cars",
            field=models.ManyToManyField(through="employees.DriverCar", to="employees.car", verbose_name="Автомобили"),
        ),
        migrations.CreateModel(
            name="Waybill",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("departure_time", models.DateTimeField(verbose_name="Время выезда")),
                ("arrival_time", models.DateTimeField(verbose_name="Время заезда")),
                ("start_mileage", models.PositiveIntegerField(verbose_name="Начальный километраж")),
                ("end_mileage", models.PositiveIntegerField(verbose_name="Конечный километраж")),
                ("car", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="employees.car", verbose_name="Автомобиль")),
                ("driver", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="employees.driver", verbose_name="Водитель")),
            ],
            options={
                "verbose_name": "Путевой лист",
                "verbose_name_plural": "Путевые листы",
                "ordering": ("-departure_time",),
            },
        ),
    ]
