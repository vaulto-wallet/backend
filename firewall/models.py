from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from transfers.models import TransferRequest
from datetime import datetime, timedelta



class FirewallAddress(models.Model):
    address = models.CharField(max_length=255)
    firewall_rule = models.ForeignKey("firewall.FirewallRule", on_delete=models.CASCADE)


class FirewallRuleSignatures(models.Model):
    firewall_rule = models.ForeignKey("firewall.FirewallRule", on_delete=models.CASCADE)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)


class FirewallRule(models.Model):
    private_key = models.ForeignKey("keys.PrivateKey", on_delete=models.CASCADE)
    amount = models.FloatField(default=0, blank=True)
    signatures_required = models.IntegerField(default=1)
    period = models.IntegerField(default=0, blank=True, null=True)

    @property
    def address_list(self):
        return FirewallAddress.objects.filter(firewall_rule=self)

    @property
    def firewall_signatures(self):
        return FirewallRuleSignatures.objects.filter(firewall_rule=self)

    @property
    def sent_amount(self):
        if self.period == 0:
            return 0
        transfers = TransferRequest.objects.filter(firewall_rule = self, executed_at__gte=datetime.now() - timedelta(hours=self.period)).\
            aggregate(total_amount=Sum('outs__amount')).get("total_amount", 0)
        return transfers

