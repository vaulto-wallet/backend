from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AssetSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import permissions
from.models import Asset
from Crypto.PublicKey import RSA
from django.http import JsonResponse
from django.core import serializers


class AssetView(generics.RetrieveAPIView):
    serializer_class = AssetSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request, *args, **kwargs):
        serializer = AssetSerializer(data=request.data)
        if serializer.is_valid():
            new_asset = serializer.save()
            new_asset.coin_index |= 0x80000000
            new_asset.save()
            if new_asset:
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, *args, **kwargs):
        type_choices = Asset._meta.get_field('asset_type').choices

        if Asset.objects.all().count() == 0:
            return JsonResponse({"assets": None, 'types' : type_choices})
        models = Asset.objects.all()
        response = {}
        for current_model in models:
            serialized = AssetSerializer(current_model).data
            response[current_model.symbol] = serialized
        return JsonResponse({"assets" : response, 'types' : type_choices})

