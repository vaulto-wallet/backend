from rest_framework import serializers
from .models import Address
from rest_framework.validators import UniqueValidator

class CustomUniqueValidator(UniqueValidator):
    def filter_queryset(self, value, queryset):
        filter_kwargs = {"private_key" : self.private_key}
        return queryset.filter(**filter_kwargs)

class AddressSerializer(serializers.ModelSerializer):
    n = serializers.IntegerField(
        validators=[CustomUniqueValidator(queryset=Address.objects.all())]
    )

    class Meta:
        model = Address
        fields = ('id', 'address', 'address_addon', 'address_type', 'balance', 'n', 'private_key')
