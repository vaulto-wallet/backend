# Generated by Django 2.2.1 on 2019-06-10 13:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('firewall', '0004_auto_20190527_1541'),
        ('transfers', '0004_transferrequest_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='transferrequest',
            name='created_at',
            field=models.DateTimeField(auto_now=True, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='transferrequest',
            name='executed_at',
            field=models.DateTimeField(blank=True, null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transferrequest',
            name='firewall_rule',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='firewall.FirewallRule'),
        ),
    ]