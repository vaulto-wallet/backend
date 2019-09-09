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

        # URL for creating an account.
        self.create_url = reverse('account-create')
        self.create_key_url = reverse('key-create')
        self.login_url = '/api/user/login/'
        self.create_privkey= reverse('privkey-create')

        #Asset(symbol="BTC", decimals=10, asset_type=Asset.ASSET_TYPE_BASE, coin_index=0x80000000, name="Bitcoin").save()

    def test_create_user(self):
        """
        Ensure we can create a new user and a valid token is created with it.
        """
        data = {
            'username': 'foobar',
            'email': 'foobar@example.com',
            'password': 'somepassword'
        }

        response = self.client.post(self.create_url , data, format='json')

        # We want to make sure we have two users in the database..
        self.assertEqual(User.objects.count(), 2)
        # And that we're returning a 201 created code.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Additionally, we want to return the username and email upon successful creation.
        self.assertEqual(response.data['username'], data['username'])
        self.assertEqual(response.data['email'], data['email'])
        self.assertFalse('password' in response.data)

    def test_create_user_with_short_password(self):
        """
        Ensure user igs not created for password lengths less than 8.
        """
        data = {
            'username': 'foobar',
            'email': 'foobarbaz@example.com',
            'password': 'foo'
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['password']), 1)

    def test_create_user_with_no_password(self):
        data = {
            'username': 'foobar',
            'email': 'foobarbaz@example.com',
            'password': ''
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['password']), 1)

    def test_create_user_with_too_long_username(self):
        data = {
            'username': 'foo' * 30,
            'email': 'foobarbaz@example.com',
            'password': 'foobar'
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['username']), 1)

    def test_create_user_with_no_username(self):
        data = {
            'username': '',
            'email': 'foobarbaz@example.com',
            'password': 'foobar'
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['username']), 1)

    def test_create_user_with_preexisting_username(self):
        data = {
            'username': 'testuser',
            'email': 'user@example.com',
            'password': 'testuser'
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['username']), 1)

    def test_create_user_with_preexisting_email(self):
        data = {
            'username': 'testuser2',
            'email': 'test@example.com',
            'password': 'testuser'
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)

    def test_create_user_with_invalid_email(self):
        data = {
            'username': 'foobarbaz',
            'email': 'testing',
            'passsword': 'foobarbaz'
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)

    def test_create_user_with_no_email(self):
        data = {
            'username': 'foobar',
            'email': '',
            'password': 'foobarbaz'
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)

    def test_create_user_and_key(self):
        """
        Ensure we can create a new user and a valid token is created with it.
        """
        data = {
            'username': 'foobar',
            'email': 'asda@asdf.com',
            'password': 'somepassword'
        }

        response = self.client.post(self.create_url , data, format='json')
        response_json = json.loads(response.content)
        data = {
            "username" : response_json["username"],
            "password": 'somepassword'
        }

        response = self.client.post(self.login_url , data, format='json')
        response_json = json.loads(response.content)

        session_key = response_json["key"]

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + session_key)

        data={
        }

        response = self.client.get(reverse("assets"), data, format='json')
        print(f'GET ASSETS  {response.status_code} {response.content}')

        data={
            'symbol' : "BTC",
            'decimals' : 10,
            'rounding' : 8,
            'coin_index' : 0x80000000,
            'name' : "Bitcoin"
        }
        response = self.client.post(reverse("assets"), data, format='json')
        print(f'POST ASSETS  {response.status_code} {response.content}')

        response = self.client.get(reverse("assets"), data, format='json')
        print(f'GET ASSETS  {response.status_code} {response.content}')

        data={
            'symbol' : "ETH",
            'decimals' : 10,
            'rounding' : 8,
            'coin_index' : 0x80000000,
            'name' : "ETHEREUM"
        }
        response = self.client.post(reverse("assets"), data, format='json')
        print(f'POST ASSETS  {response.status_code} {response.content}')

        response = self.client.get(reverse("assets"), data, format='json')
        print(f'GET ASSETS  {response.status_code} {response.content}')


        data = {
        }
        response = self.client.get(self.create_key_url, data, format='json')
        print(f'GET ACCOUNT  {response.status_code} {response.content}')

        data = {
            'master_password' : 'masterpwd'
        }


        response = self.client.post(self.create_key_url, data, format='json')

        # We want to make sure we have two users in the database..
        self.assertEqual(User.objects.count(), 2)
        # And that we're returning a 201 created code.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Additionally, we want to return the username and email upon successful creation.

        data = {
            'private_key_type' : 1,
            'name' : "Key #1",
            'asset' : "BTC",
        }

        response = self.client.post("/api/keys/", data, format='json')
        print(response)


        data = {
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + session_key)
        response = self.client.get(self.create_key_url, data, format='json')
        print(f'GET ACCOUNT  {response.status_code} {response.content}')


        data = {
            'master_password': 'masterpwd',
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

        data = {
            'key': session_key,
        }
        get_address_url = reverse("address-get", kwargs={"pk":2, "n":1})
        response = self.client.post(get_address_url, data, format='json')
        print(response)
        get_address_url = reverse("address-get", kwargs={"pk":2, "n":2})
        response = self.client.post(get_address_url, data, format='json')
        print(response)

        scan()

        res = ping.delay(1)
        print(res)
        res = scan.delay()
        print(res)
        time.sleep(5)

        pkeys = PrivateKey.objects.all()
        for p in pkeys:
            print(p, p.balance)

        get_address_url = reverse("addresses-get", kwargs={"pk":2})
        response = self.client.get(get_address_url, data, format='json')
        print(response.content)


    def test_create_users_and_share_key(self):
        userlist = {
            "user1" : {
                "name" : "User1 Name",
                "email" : "user1@test.com",
                "password": "password1",
                "master_password": "masterPwd1",
            },
            "user2": {
                "name": "User2 Name",
                "email": "user2@test.com",
                "password": "password2",
                "master_password": "masterPwd2",
            },
            "user3": {
                "name": "User3 Name",
                "email": "user3@test.com",
                "password": "password3",
                "master_password": "masterPwd3",
            },
            "user4": {
                "name": "User4 Name",
                "email": "user4@test.com",
                "password": "password4",
                "master_password": "masterPwd4",
            },
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

        print("Share to 3,4")
        data = {
            'master_password': userdata["master_password"],
            'id': 2,
            'share_to' : [3, 4]
        }

        response = self.client.post("/api/keys/share/", data, format='json')
        print(response.content)

        pkeys = PrivateKey.objects.all()
        for p in pkeys:
            print(p)

        print("Share to 3,4")
        data = {
            'master_password': userdata["master_password"],
            'id': 2,
            'share_to' : [3, 4]
        }

        response = self.client.post("/api/keys/share/", data, format='json')
        print(response.content)

        pkeys = PrivateKey.objects.all()
        for p in pkeys:
            print(p)


        print("Share to 3,5")
        data = {
            'master_password': userdata["master_password"],
            'id': 2,
            'share_to' : [3, 5]
        }

        response = self.client.post("/api/keys/share/", data, format='json')
        print(response.content)

        pkeys = PrivateKey.objects.all()
        for p in pkeys:
            print(p)
