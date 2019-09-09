from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Asset


class AssetSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(
            required=True,
            validators=[UniqueValidator(queryset=Asset.objects.all())]
            )

    class Meta:
        model = Asset
        fields = ('symbol', 'coin_index', 'asset_type', 'decimals', 'rounding', 'asset_address', 'name')
