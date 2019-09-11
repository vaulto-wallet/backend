from django.db import models
from django.db.models import Sum
import struct

class Confirmation(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, null=True)
    status = models.BooleanField(default=False)
    request = models.ForeignKey("transfers.TransferRequest", on_delete=models.CASCADE)
    code_2fa = models.CharField(max_length=255, blank=True, null=True)
    signature = models.CharField(max_length=255, blank=True, null=True)
    validated = models.BooleanField(default=False)

class Out(models.Model):
    address = models.CharField(max_length=255)
    amount = models.FloatField(default=0)
    request = models.ForeignKey("transfers.TransferRequest", on_delete=models.CASCADE)
    @property
    def binary(self):
        res = bytearray(struct.pack("f", self.amount)) + len(self.address).to_bytes(4, byteorder='little') + self.address.encode("ascii")
        return res

class TransferRequest(models.Model):
    STATUS_NO_FIREWALL_RULE = 1
    STATUS_CREATED = 2
    STATUS_NEED_SIGN = 3
    STATUS_SIGNED = 4
    STATUS_CANCELLED = 5
    STATUS_PENDING_TRANSACTION = 6
    STATUS_PROCESSED = 7


    user = models.ForeignKey("auth.User", related_query_name="user", on_delete=models.CASCADE, default=0)
    private_key = models.ForeignKey('keys.PrivateKey', on_delete=models.CASCADE)
    status = models.IntegerField(default=0)
    description = models.CharField(max_length=255, blank=True, null=True)
    firewall_rule = models.ForeignKey('firewall.FirewallRule', blank=True, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    executed_at = models.DateTimeField(blank=True, null=True)

    @property
    def outs(self):
        return Out.objects.filter(request=self)

    @property
    def confirmations(self):
        return Confirmation.objects.filter(request=self)

    @property
    def related_users(self):
        result = [self.user]
        if self.firewall_rule:
            for fr in self.firewall_rule.firewall_signatures:
                result.append(fr.user)
        return result
    @property
    def binary(self):
        res = len(self.outs).to_bytes(4, byteorder="little")
        for o in self.outs:
            res += o.binary
        return res



    @property
    def total_amount(self):
        return self.out_set.aggregate(Sum("amount")).get("amount_sum", 0)

    def outs_math_rule(self, outs_address_list, firewall_address_list):
        if "*" in firewall_address_list:
            return 1
        for o in outs_address_list:
            if o not in firewall_address_list:
                return 0
        return 2


    def set_firewall_rule(self):
        current_key  = self.private_key
        if current_key.parent_key != None and current_key.parent_key.private_key_type == current_key.KEY_TYPE_ROOT:
            current_key = current_key.parent_key

        address_match_wildcard = []
        address_match_full = []

        out_addresses = [o.address for o in self.out_set.all()]
        firewall_rules = current_key.firewall_rules.all()
        for fr in firewall_rules:
            firewall_addresses = [ fa.address for fa in fr.address_list]
            match_result = self.outs_math_rule(out_addresses, firewall_addresses)
            if match_result == 1:
                address_match_wildcard.append(fr)
            if match_result == 2:
                address_match_full.append(fr)

        rules_set  = address_match_wildcard
        if len(address_match_full) > 0 :
            rules_set = address_match_full

        limited_rule = None
        unlimited_rule = None
        for r in rules_set:
            if r.amount == "*":
                unlimited_rule = r
            else:
                if limited_rule is None or (limited_rule.amount > r.amount and r.sent_amount() +  self.total_amount <= r.amount ):
                    limited_rule = r

        if limited_rule:
            self.firewall_rule = limited_rule
        if unlimited_rule:
            self.firewall_rule = unlimited_rule

        if self.firewall_rule is None:
            self.status = self.STATUS_NO_FIREWALL_RULE



