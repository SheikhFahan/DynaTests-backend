# Generated by Django 4.1 on 2024-01-30 05:06

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('group_tests', '0004_rename_testpassword_subtestsessionpassword_and_more'),
        ('user_profiles', '0002_remove_attendancecategorysession_institute_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='attendancecategorysession',
            unique_together={('candidate', 'session', 'unique_id')},
        ),
        migrations.AlterUniqueTogether(
            name='attendanceccsession',
            unique_together={('candidate', 'session', 'unique_id')},
        ),
        migrations.AlterUniqueTogether(
            name='attendancesubtest',
            unique_together={('candidate', 'session', 'unique_id')},
        ),
    ]