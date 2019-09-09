from django.db import models


class Asset(models.Model):
    ASSET_TYPE_BASE = 1
    ASSET_TYPE_ERC20 = 2

    ASSET_TYPE_CHOICES = (
        (ASSET_TYPE_BASE, "BASIC"),
        (ASSET_TYPE_BASE, "ERC20"),
    )

    coin_index = models.IntegerField(blank=True, null=True)
    symbol = models.CharField(max_length=255, unique=True)
    asset_type = models.IntegerField(choices=ASSET_TYPE_CHOICES, default=ASSET_TYPE_BASE)
    decimals = models.IntegerField()
    rounding = models.IntegerField(default=8)
    asset_address = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)

