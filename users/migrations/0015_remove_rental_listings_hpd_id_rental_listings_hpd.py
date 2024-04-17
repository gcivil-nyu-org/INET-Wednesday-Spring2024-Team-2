# Generated by Django 4.2 on 2024-04-16 23:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0014_rename_hpd_rental_listings_hpd_id"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="rental_listings",
            name="HPD_id",
        ),
        migrations.AddField(
            model_name="rental_listings",
            name="HPD",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="users.usershpddata",
            ),
        ),
    ]
