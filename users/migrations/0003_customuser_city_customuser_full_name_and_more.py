# Generated by Django 4.2 on 2024-03-08 21:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_alter_customuser_groups_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="city",
            field=models.CharField(default="New York City", max_length=100),
        ),
        migrations.AddField(
            model_name="customuser",
            name="full_name",
            field=models.CharField(default="FullNameDefault", max_length=255),
        ),
        migrations.AddField(
            model_name="customuser",
            name="phone_number",
            field=models.CharField(default="9999999999", max_length=15),
        ),
    ]