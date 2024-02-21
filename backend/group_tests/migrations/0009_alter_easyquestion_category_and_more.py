# Generated by Django 4.1 on 2024-02-17 09:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('group_tests', '0008_alter_hardquestion_test_alter_mediumquestion_test'),
    ]

    operations = [
        migrations.AlterField(
            model_name='easyquestion',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='easy_question', to='group_tests.grouptestcategory'),
        ),
        migrations.AlterField(
            model_name='hardquestion',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hard_question', to='group_tests.grouptestcategory'),
        ),
        migrations.AlterField(
            model_name='mediumquestion',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='medium_question', to='group_tests.grouptestcategory'),
        ),
    ]