from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.contrib.auth.models import User
from keys.models import PrivateKey
from address.models import Address

@shared_task
def ping(x):
    return x+1

@shared_task
def scan():
    addresses = Address.objects.all()
    for current_address in addresses:
        print(f'{current_address.address}  {current_address.private_key}')
        current_address.balance = 100000000000
        current_address.save()
