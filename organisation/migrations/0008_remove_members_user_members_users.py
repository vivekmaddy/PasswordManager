# Generated by Django 4.2.5 on 2023-09-13 09:30

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organisation', '0007_members'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='members',
            name='user',
        ),
        migrations.AddField(
            model_name='members',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
