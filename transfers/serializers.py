from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Out, Confirmation, TransferRequest
import struct

class OutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Out
        fields = ("address", "amount")

class ConfirmationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Confirmation
        fields= ("user", "status", "request", "code_2fa", "signature")

class TransferRequestSerializer(serializers.ModelSerializer):
    outs = OutSerializer(many=True)
    confirmations = ConfirmationSerializer(many=True, required=False)

    is_confirmed = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()

    class Meta:
        model = TransferRequest
        fields = ('id', 'user', 'private_key', 'status', 'outs', 'confirmations', 'description', 'firewall_rule', 'is_confirmed', 'currency')
        read_only_fields = ('is_confirmed', 'currency', 'binary_outs')


    def get_currency(self, obj):
        return obj.private_key.asset.symbol

    def get_is_confirmed(self, obj):
        request_user_id = self.context.get("request_user", None)
        if request_user_id is None:
            return False
        for c in obj.confirmations:
            if c.user == request_user_id:
                return True
        #if request_user_id == obj.user:
        #    return True

        return False


    def create(self, validated_data):
        request_model = TransferRequest(user=validated_data["user"], private_key=validated_data["private_key"], description=validated_data["description"])

        request_model.save()
        outs = validated_data.pop("outs")
        for o in outs:
            request_model.out_set.create(**o)

        request_model.set_firewall_rule()
        request_model.save()

        return request_model
