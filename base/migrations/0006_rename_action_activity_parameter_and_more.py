# Generated by Django 4.1.6 on 2023-04-03 04:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0005_activity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='activity',
            old_name='action',
            new_name='parameter',
        ),
        migrations.RemoveField(
            model_name='activity',
            name='staff',
        ),
        migrations.AddField(
            model_name='activity',
            name='user',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]