from django.db import models

class Address(models.Model):
    ADDRESS_TYPE_OWN = 1
    ADDRESS_TYPE_FOREIGN = 2

    ADDRESS_TYPE_CHOICE = (
        (ADDRESS_TYPE_OWN, "OWN"),
        (ADDRESS_TYPE_FOREIGN, "FOREIGN")
    )
    address = models.CharField(max_length=255)
    address_addon = models.CharField(max_length=255, blank=True, null=True)
    private_key = models.ForeignKey("keys.PrivateKey", on_delete=models.CASCADE, blank=True)
    address_type = models.IntegerField(default=ADDRESS_TYPE_OWN, choices=ADDRESS_TYPE_CHOICE)
    balance = models.BigIntegerField(default=0)
    n = models.IntegerField()
