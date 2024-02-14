# Generated by Django 4.1 on 2024-01-26 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group_tests', '0003_categorytestsession_duration_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TestPassword',
            new_name='SubTestSessionPassword',
        ),
        migrations.RenameField(
            model_name='subtestsessionpassword',
            old_name='test',
            new_name='session',
        ),
        migrations.AlterField(
            model_name='categorytestsession',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='combinedcategorytestsession',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='subtestsession',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]