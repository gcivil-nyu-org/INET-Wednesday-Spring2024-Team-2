# Generated by Django 4.2 on 2024-04-17 00:34

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0021_remove_rental_listings_hpd_rental_listings_hpd_data"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="rental_listings",
            name="hpd_data",
        ),
    ]