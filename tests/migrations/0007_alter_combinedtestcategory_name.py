# Generated by Django 4.1 on 2024-02-16 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0006_remove_test_easy_test_file_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='combinedtestcategory',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]