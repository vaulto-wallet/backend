# Generated by Django 2.2.1 on 2019-06-10 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transfers', '0005_auto_20190610_1350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transferrequest',
            name='created_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='transferrequest',
            name='executed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
