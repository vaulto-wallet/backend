from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User, Group
from .models import Account
from Crypto.PublicKey import RSA


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=False,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    username = serializers.CharField(
        max_length=32,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(min_length=8, write_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'],
             validated_data['password'])
        return user



    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'groups')
        write_only_fields = ('password',)

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')

class AccountSerializer(serializers.ModelSerializer):

    private_key = serializers.CharField(
                max_length=255,
                required=False,
                write_only=True
            )
    public_key = serializers.CharField(
                max_length=255,
                required=False,
            )
    name = serializers.CharField(
                max_length=60,
                required=False,
    )
    user = serializers.PrimaryKeyRelatedField(
        many=False, queryset=User.objects.all(),
        validators = [UniqueValidator(queryset=Account.objects.all())]
    )

    class Meta:
        model = Account
        fields = ( 'user', 'private_key', 'public_key', 'name')
