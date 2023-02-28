# Generated by Django 4.1.6 on 2023-02-28 09:35

from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('access', models.CharField(choices=[('STAFF', 'Staff'), ('STUDENT', 'Student')], default='STAFF', max_length=7)),
                ('username', models.EmailField(max_length=254, unique=True)),
                ('avatar', models.ImageField(default='avatar.svg', null=True, upload_to='')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=100)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('text', models.TextField(max_length=1000, validators=[django.core.validators.MinLengthValidator(50)])),
                ('is_good', models.BooleanField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited', models.BooleanField(default=False)),
                ('deleted', models.BooleanField(default=False)),
                ('leadership', models.IntegerField(default=0)),
                ('respect', models.IntegerField(default=0)),
                ('punctuality', models.IntegerField(default=0)),
                ('participation', models.IntegerField(default=0)),
                ('teamwork', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('faculty', models.CharField(max_length=100, null=True)),
                ('department', models.CharField(max_length=100, null=True)),
                ('prefix', models.CharField(choices=[('Prof.', 'Prof.'), ('Dr.', 'Dr.'), ('Mrs.', 'Mrs.'), ('Ms.', 'Mrs.'), ('Mr.', 'Mr.'), ('Mx.', 'Mx.')], default='Mx.', max_length=5)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('faculty', models.CharField(max_length=100)),
                ('department', models.CharField(max_length=100)),
                ('bio', models.TextField(max_length=500, null=True)),
                ('lectured_by', models.ManyToManyField(to='base.staff')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('value', models.CharField(choices=[('UP', 'Upvote'), ('DOWN', 'Downvote')], max_length=4)),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.review')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.staff')),
            ],
        ),
        migrations.CreateModel(
            name='Student_Inbox',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('message', models.TextField(max_length=50)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.student')),
            ],
        ),
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('leadership', models.IntegerField(default=0)),
                ('respect', models.IntegerField(default=0)),
                ('punctuality', models.IntegerField(default=0)),
                ('participation', models.IntegerField(default=0)),
                ('teamwork', models.IntegerField(default=0)),
                ('student', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.student')),
            ],
        ),
        migrations.CreateModel(
            name='Staff_Inbox',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
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
    ]
