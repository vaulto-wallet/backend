# Generated by Django 2.2.1 on 2019-05-27 15:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('firewall', '0003_firewallrulesignatures'),
    ]

    operations = [
        migrations.AlterField(
            model_name='firewalladdress',
            name='firewall_rule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='firewall.FirewallRule'),
        ),
    ]