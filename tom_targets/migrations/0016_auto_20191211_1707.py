# Generated by Django 2.2.8 on 2019-12-11 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tom_targets', '0015_auto_20190923_2233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='targetextra',
            name='value',
            field=models.TextField(blank=True, default=''),
        ),
    ]
