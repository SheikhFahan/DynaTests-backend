# Generated by Django 4.1 on 2024-02-04 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.CharField(default='Defalult Description a quick brown fox jumps over a lazy dog.', max_length=100),
        ),
    ]