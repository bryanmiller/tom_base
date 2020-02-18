# Generated by Django 2.2.9 on 2020-01-30 23:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tom_targets', '0015_auto_20190923_2233'),
    ]

    operations = [
        migrations.AddField(
            model_name='target',
            name='epoch_of_elements',
            field=models.FloatField(blank=True, help_text='Julian date.', null=True, verbose_name='Epoch of Elements'),
        ),
        migrations.AlterField(
            model_name='target',
            name='epoch',
            field=models.FloatField(blank=True, help_text='Julian Years. Max 2100.', null=True, verbose_name='Epoch'),
        ),
    ]
