# Generated by Django 4.1.6 on 2023-04-05 00:06

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=1000, validators=[django.core.validators.MinLengthValidator(50)])),
                ('rating', models.IntegerField(default=3)),
                ('is_good', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('edited', models.BooleanField(default=False)),
                ('deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_pic', models.ImageField(default='avatar.svg', null=True, upload_to='')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.school')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('active', models.BooleanField(default=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.school')),
            ],
        ),
        migrations.CreateModel(
            name='EndorsementStats',
            fields=[
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='base.student')),
            ],
        ),
        migrations.CreateModel(
            name='Karma',
            fields=[
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='base.student')),
                ('score', models.IntegerField(default=100)),
            ],
        ),
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('review', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='base.review')),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('value', models.CharField(choices=[('UP', 'Upvote'), ('DOWN', 'Downvote')], max_length=4)),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.review')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.staff')),
            ],
        ),
        migrations.CreateModel(
            name='Staff_Inbox',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(max_length=50)),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.staff')),
            ],
        ),
        migrations.AddField(
            model_name='review',
            name='staff',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.staff'),
        ),
        migrations.AddField(
            model_name='review',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.student'),
        ),
        migrations.CreateModel(
            name='Endorsement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leadership', models.BooleanField(default=False)),
                ('respect', models.BooleanField(default=False)),
                ('punctuality', models.BooleanField(default=False)),
                ('participation', models.BooleanField(default=False)),
                ('teamwork', models.BooleanField(default=False)),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.staff')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.student')),
            ],
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.school')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('parameter', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
