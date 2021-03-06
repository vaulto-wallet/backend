# Generated by Django 2.2.1 on 2019-05-26 11:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrivateKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('private_key', models.CharField(blank=True, max_length=255, null=True)),
                ('public_key', models.CharField(blank=True, max_length=255, null=True)),
                ('private_key_type', models.IntegerField(choices=[(1, 'SEED'), (2, 'ROOT'), (3, 'SINGLE'), (4, 'MULTI')], default=1)),
                ('network_type', models.CharField(choices=[('main', 'MainNet'), ('testnet', 'TestNet')], default='main', max_length=255)),
                ('asset', models.ForeignKey(blank=True, db_column='asset', null=True, on_delete=django.db.models.deletion.CASCADE, to='assets.Asset', to_field='symbol')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owner', related_query_name='user', to=settings.AUTH_USER_MODEL)),
                ('parent_key', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='keys.PrivateKey')),
            ],
        ),
    ]
