# Generated by Django 5.1.5 on 2025-03-04 13:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_users_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='users',
            name='slug',
        ),
    ]
