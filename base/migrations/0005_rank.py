# Generated by Django 4.1.6 on 2023-03-21 21:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_rename_endstats_endorsementstats'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rank',
            fields=[
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='base.student')),
            ],
        ),
    ]
