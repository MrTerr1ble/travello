# Generated by Django 4.2 on 2025-04-05 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("trail", "0005_rename_location_pointsofinterest_latitude_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="routers",
            name="created_at",
            field=models.DateField(
                auto_now_add=True, verbose_name="Дата создания маршрута"
            ),
        ),
    ]
