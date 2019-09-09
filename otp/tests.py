from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from otp.models import OTP
from django_otp.oath import TOTP
import json
import base64


class OTPTest(APITestCase):
    def setUp(self):
        # We want to go ahead and originally create a user.
        self.test_user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        data = {
            "username": self.test_user.username,
            "password": "testpassword"
        }
        response = self.client.post('/api/user/login/', data, format='json')
        response_json = json.loads(response.content)
        self.session_key  = response_json["key"]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.session_key)

    def test_create_otp(self):
        data = {
        }
        response = self.client.get("/api/otp/", data, format='json')
        print(response.content)
        resp = json.loads(response.content)
        token = TOTP(key=base64.b32decode(resp["secret"])).token()
        print(token)

        data = {
            "code" : token
        }
        response = self.client.post("/api/otp/", data, format='json')
        print(response.content)

        data = {
        }
        response = self.client.get("/api/otp/", data, format='json')
        print(response.content)
