from django.db import models
from django.contrib.auth.models import User
from transfers.models import Confirmation

class OTP(models.Model):
    user = models.OneToOneField(to="auth.User", on_delete=models.CASCADE)
    secret = models.CharField(max_length=255)
    validated = models.BooleanField(default=False)

