# Generated by Django 4.1 on 2024-01-25 16:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('group_tests', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grouptest',
            name='has_password',
        ),
        migrations.CreateModel(
            name='SubTestSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15)),
                ('has_password', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('sub_test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='group_tests.grouptest')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='testpassword',
            name='test',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='password_info', to='group_tests.subtestsession'),
        ),
    ]
