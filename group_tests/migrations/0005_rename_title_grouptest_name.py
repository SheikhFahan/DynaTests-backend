# Generated by Django 4.1 on 2024-02-06 06:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group_tests', '0004_rename_testpassword_subtestsessionpassword_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='grouptest',
            old_name='title',
            new_name='name',
        ),
    ]
