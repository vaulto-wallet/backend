from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import permissions
from .models import OTP
from .serializers import OTPSerializer
from django_otp import util as otp_util
from django_otp.oath import TOTP
import base64


from django.http import JsonResponse
import binascii

from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt


class OTPView(generics.RetrieveAPIView):
    serializer_class = OTPSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request, *args, **kwargs):
        code = request.data.get("code", None)
        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        model = OTP.objects.get(user=request.user)
        if model is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if model.validated:
            return Response(status=status.HTTP_423_LOCKED)
        if TOTP(base64.b32decode(model.secret)).verify(code):
            model.validated = True
            model.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        request.data.update({"user" : request.user.id})

        if not hasattr(request.user, "otp"):
            new_otp = OTP(user=request.user, secret=base64.b32encode(binascii.a2b_hex(otp_util.random_hex(10))).decode(), validated=0)
            new_otp.save()

        model = request.user.otp
        if model is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if model.validated:
            return JsonResponse({"validated": True}, status=status.HTTP_200_OK)

        return JsonResponse({"validated" : False, "secret" : model.secret}, status=status.HTTP_200_OK)
