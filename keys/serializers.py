from rest_framework import serializers
from .models import PrivateKey
from accounts.serializers import AccountSerializer
from django.contrib.auth.models import User
from assets.models import Asset
from keys.models import PrivateKey
from address.models import Address
from firewall.models import FirewallRule
from firewall.serializers import FirewallRuleSerializer

class SharedKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateKey
        fields =("id", "owner",)

class PrivateKeySerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        many=False, queryset=User.objects.all(),
    )

    private_key = serializers.CharField(
                max_length=255,
                required=False,
            )
    public_key = serializers.CharField(
                max_length=255,
                required=False,
    )
    parent_key= serializers.PrimaryKeyRelatedField(
        many=False, queryset=PrivateKey.objects.all(), required=False
    )

    assetname = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    shared_keys = SharedKeySerializer(many=True, required=False)
    n = serializers.SerializerMethodField()
    firewall_rules = serializers.SerializerMethodField()

    def get_balance(self, obj):
        model = PrivateKey.objects.get(pk = obj.id)
        if model is None:
            return 0
        if model.private_key_type == PrivateKey.KEY_TYPE_SEED:
            return None
        return round(model.balance / (pow(10, model.asset.decimals)), model.asset.rounding)

    def get_shared_keys(self, obj):
        if obj.private_key_type == PrivateKey.KEY_TYPE_SEED:
            return[]
        return obj.shared_keys

    def get_n(self, obj):
        if obj.private_key_type == PrivateKey.KEY_TYPE_ROOT:
            return Address.objects.filter(private_key=obj).count()
        return 0

    def get_firewall_rules(self, obj):
        if obj.private_key_type == PrivateKey.KEY_TYPE_ROOT:
            objects = FirewallRule.objects.filter(private_key=obj)
            if objects.count() == 0:
                return None
            return FirewallRuleSerializer(objects,many=True).data
        return 0

    def get_assetname(self, obj):
        if obj.asset is None:
            return None
        return obj.asset.name


    class Meta:
        model = PrivateKey
        fields = ('id', 'name', 'owner', 'private_key', 'private_key_type', 'parent_key', 'public_key', 'asset', 'assetname', "network_type", "balance", "shared_keys", "n", "firewall_rules")

    def create(self, validated_data):
        return PrivateKey.objects.create(** validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        return instance

    def validate(self, data):
        if data['private_key_type'] in [PrivateKey.KEY_TYPE_ROOT, PrivateKey.KEY_TYPE_SINGLE, PrivateKey.KEY_TYPE_MULTI]:
            if not data.get('asset', None):
                raise serializers.ValidationError("Asset must be provided for this type of key")
        return data
'''
class UserSerializer(serializers.ModelSerializer):
    keys = serializers.PrimaryKeyRelatedField(many=True, queryset=PrivateKey.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'keys', 'owner')
'''