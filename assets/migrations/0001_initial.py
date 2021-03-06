# Generated by Django 2.2.1 on 2019-05-26 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coin_index', models.IntegerField(blank=True, null=True)),
                ('symbol', models.CharField(max_length=255, unique=True)),
                ('asset_type', models.IntegerField(choices=[(1, 'BASIC'), (1, 'ERC20')], default=1)),
                ('decimals', models.IntegerField()),
                ('rounding', models.IntegerField(default=8)),
                ('asset_address', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]
