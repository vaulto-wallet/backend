from django.db import models
from django.contrib.auth.models import User
from otp.models import OTP

class Account(models.Model):
    name = models.CharField(max_length=255)
    private_key = models.CharField(max_length=255)
    public_key = models.CharField(max_length=255)
    user = models.OneToOneField(to="auth.User", on_delete=models.CASCADE)

    @property
    def otp(self):
        return OTP.objects.get(user=self.user)

    def __str__(self):
        return f'{self.name}  {self.user}'


