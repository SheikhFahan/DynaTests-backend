# Generated by Django 4.1 on 2024-02-22 05:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('group_tests', '0014_alter_grouptest_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categorytestsessionscoresummary',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='group_tests.categorytestsession'),
        ),
        migrations.AlterField(
            model_name='ccsessionscoresummary',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='group_tests.combinedcategorytestsession'),
        ),
        migrations.AlterField(
            model_name='subtestsessionscoresummary',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='group_tests.subtestsession'),
        ),
    ]
