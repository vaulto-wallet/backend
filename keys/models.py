from django.db import models
from django.db.models import Sum
from address.models import Address
from firewall.models import FirewallRule

class PrivateKey(models.Model):
    KEY_TYPE_SEED = 1
    KEY_TYPE_ROOT = 2
    KEY_TYPE_SINGLE = 3
    KEY_TYPE_MULTI = 4

    NETWORK_TYPE_MAIN = "main"
    NETWORK_TYPE_TESTNET = "testnet"

    NETWORK_TYPE_CHOICES = (
        (NETWORK_TYPE_MAIN, "MainNet"),
        (NETWORK_TYPE_TESTNET, "TestNet")
    )

    KEY_TYPE_CHOICES = (
        (KEY_TYPE_SEED, 'SEED'),
        (KEY_TYPE_ROOT, 'ROOT'),
        (KEY_TYPE_SINGLE, 'SINGLE'),
        (KEY_TYPE_MULTI, 'MULTI')
    )

    name = models.CharField(max_length=255)
    private_key = models.CharField(max_length=255, blank=True, null=True)
    public_key = models.CharField(max_length=255, blank=True, null=True)
    private_key_type = models.IntegerField(default=1, choices=KEY_TYPE_CHOICES)
    owner = models.ForeignKey('auth.User', related_name='owner', related_query_name="user" , on_delete=models.CASCADE)
    parent_key = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    asset = models.ForeignKey("assets.Asset", on_delete=models.CASCADE, to_field="symbol", db_column="asset", blank=True, null=True)
    network_type = models.CharField(max_length=255, default="main", choices=NETWORK_TYPE_CHOICES)
    shared_keys = models.ManyToManyField('auth.User')

    @property
    def balance(self):
        balance_sum = Address.objects.filter(private_key=self).aggregate(Sum("balance")).get('balance__sum', None)
        if balance_sum is None:
            return 0
        return balance_sum
    '''
    @property
    def shared_keys(self):
        return PrivateKey.objects.filter(parent_key=self)
    '''

    @property
    def firewall_rules(self):
        return FirewallRule.objects.filter(private_key=self)


    def __str__(self):
        return str(self.id) + " " + self.name + " " + str(self.owner) + " " + str(self.get_private_key_type_display())



# Create your cryptoassets here.
