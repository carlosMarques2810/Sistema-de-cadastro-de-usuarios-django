# Generated by Django 5.1.5 on 2025-03-05 01:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_remove_users_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='is_active',
            field=models.BooleanField(default=False, verbose_name='active'),
        ),
    ]
