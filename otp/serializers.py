from rest_framework import serializers
from django.contrib.auth.models import User
from .models import OTP

class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields= ("user", "code")