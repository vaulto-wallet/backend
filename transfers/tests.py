from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework import status
import json
from keys.models import PrivateKey
from assets.models import Asset
from keys.tasks import ping, scan
import time

class AccountsTest(APITestCase):
    def setUp(self):
        # We want to go ahead and originally create a user.
        self.test_user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')

        self.create_url = reverse('account-create')
        self.create_key_url = reverse('key-create')
        self.login_url = '/api/user/login/'
        self.create_privkey= reverse('privkey-create')


    def test_create_user_key_transfer(self):
        userlist = {
            "user1" : {
                "name" : "User1 Name",
                "email" : "user1@test.com",
                "password": "password1",
                "master_password": "masterPwd1"
            },
            "worker": {
                "name": "Worker",
                "email": "user2@test.com",
                "password": "password2",
                "master_password": "masterPwd2"
            }
        }

        for u in userlist:
            print(f'Creating account for {u}')
            userdata = userlist[u]
            data = {
                'username': u,
                'email': userdata["email"],
                'password': userdata["password"],
            }

            response = self.client.post(self.create_url , data, format='json')
            response_json = json.loads(response.content)

            data = {
                "username" : u,
                "password": userdata["password"]
            }

            response = self.client.post(self.login_url , data, format='json')
            response_json = json.loads(response.content)

            userlist[u]["session_key"] = response_json["key"]

            self.client.credentials(HTTP_AUTHORIZATION='Token ' + userlist[u]["session_key"])

            data = {
                'master_password' : userdata['master_password']
            }

            response = self.client.post(self.create_key_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        userdata = userlist["user1"]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + userdata["session_key"])

        print("Creating BTC Asset")
        data={
            'symbol' : "BTC",
            'decimals' : 10,
            'rounding' : 8,
            'coin_index' : 0x80000000,
            'name' : "Bitcoin"
        }
        response = self.client.post(reverse("assets"), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        print("Creating Private Key for BTC")
        data = {
            'private_key_type' : 1,
            'name' : "Key #1",
            'asset' : "BTC",
        }
        response = self.client.post("/api/keys/", data, format='json')
        print(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {
            'master_password': userdata["master_password"],
            'private_key_type': 2,
            'name': "Key #2",
            'parent_key' : 1,
            'asset' : "BTC"
        }

        response = self.client.post("/api/keys/", data, format='json')
        print(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


        pkeys = PrivateKey.objects.all()
        for p in pkeys:
            print(p)

        target_address = "12312343243242"

        data = {
            'private_key' : 2,
            'address_list' : [{"address": target_address}],
            'amount' : 1,
            'period' : 24,
            'signatures_required' : 1,
            'firewall_signatures' : [{"user" : 1}]

        }

        response = self.client.post("/api/firewall/", data, format='json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {
            'private_key' : 2,
            'address_list' : [{"address": "*"}],
            'amount' : 1,
            'period' : 24,
            'signatures_required' : 1,
            'firewall_signatures' : [{"user" : 1}, {"user" : 2}]
        }

        response = self.client.post("/api/firewall/", data, format='json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



        data = {
        }

        response = self.client.get("/api/keys/", data, format='json')
        response_json = json.loads(response.content)
        print(response.content)


        data = {
            'master_password': userdata["master_password"],
            'private_key': 2,
            'outs' : [ {'address': target_address, "amount" : 0.2} , {'address': '333111223', "amount" : 0.2}],
            'description' : 'Test transfer'
        }

        response = self.client.post("/api/transfers/", data, format='json')
        print(response.content)


        data = {
            "request" : 1,
        }

        response = self.client.post("/api/transfers/confirm/", data, format='json')
        print(response.content)


        data ={}

        response = self.client.get("/api/transfers/", data, format='json')
        print(response.content)


