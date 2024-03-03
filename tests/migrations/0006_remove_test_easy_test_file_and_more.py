# Generated by Django 4.1 on 2024-02-16 05:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tests', '0005_category_user_alter_combinedtestcategory_user_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='test',
            name='easy_test_file',
        ),
        migrations.RemoveField(
            model_name='test',
            name='hard_test_file',
        ),
        migrations.RemoveField(
            model_name='test',
            name='medium_test_file',
        ),
        migrations.AlterField(
            model_name='combinedtestcategory',
            name='name',
            field=models.CharField(max_length=40),
        ),
        migrations.AlterField(
            model_name='combinedtestcategory',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]