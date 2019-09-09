from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import permissions
from .models import FirewallRule
from .serializers import FirewallRuleSerializer, FirewallAddressSerializer

from Crypto.PublicKey import RSA
from django.http import JsonResponse

from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt


class FirewallView(generics.RetrieveAPIView):
    serializer_class = FirewallRuleSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request, *args, **kwargs):
        request.data.update({"user" : request.user.id})
        serializer = FirewallRuleSerializer(data=request.data)
        if serializer.is_valid():
            new_rule = serializer.save()
            if new_rule:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        request.data.update({"user" : request.user.id})
        rule = FirewallRule.objects.get(pk=request.data["id"])
        serializer = FirewallRuleSerializer(rule, data=request.data, partial=True)
        if serializer.is_valid():
            updated_rule = serializer.save()
            if updated_rule:
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

