# Generated by Django 4.1 on 2024-02-21 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group_tests', '0013_alter_categorytestsessionscoresummary_session_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouptest',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
