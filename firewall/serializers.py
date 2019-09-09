from rest_framework import serializers
from django.contrib.auth.models import User
from .models import FirewallRule, FirewallAddress, FirewallRuleSignatures


class FirewallRuleSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirewallRuleSignatures
        fields = ("user",)


class FirewallAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirewallAddress
        fields = ("address",)


class FirewallRuleSerializer(serializers.ModelSerializer):
    address_list = FirewallAddressSerializer(many=True)
    firewall_signatures = FirewallRuleSignatureSerializer(many=True)

    class Meta:
        model = FirewallRule
        fields = ('id', 'private_key', 'signatures_required', 'firewall_signatures', 'amount', 'period', 'address_list')

    def create(self, validated_data):
        firewall_rule_model = FirewallRule(
            private_key=validated_data["private_key"],
            signatures_required=validated_data["signatures_required"],
            amount=validated_data["amount"],
            period=validated_data["period"])

        firewall_rule_model.save()

        if "address_list" in validated_data:
            address_list = validated_data.pop("address_list")
            for a in address_list:
                firewall_rule_model.firewalladdress_set.create(**a)
        if "firewall_signatures" in validated_data:
            approved = validated_data.pop("firewall_signatures")
            for a in approved:
                firewall_rule_model.firewallrulesignatures_set.create(**a)
        return firewall_rule_model

    def update(self, instance, validated_data):
        instance.signatures_required=validated_data["signatures_required"]
        instance.amount=validated_data["amount"]
        instance.period=validated_data["period"]

        instance.save()

        if instance.firewalladdress_set.count() > 0:
            instance.firewalladdress_set.all().delete()
        if instance.firewallrulesignatures_set.count() > 0:
            instance.firewallrulesignatures_set.all().delete()

        if "address_list" in validated_data:
            address_list = validated_data.pop("address_list")
            for a in address_list:
                instance.firewalladdress_set.create(**a)
        if "firewall_signatures" in validated_data:
            approved = validated_data.pop("firewall_signatures")
            for a in approved:
                instance.firewallrulesignatures_set.create(**a)
        return instance