from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import permissions
from .models import TransferRequest, Out, Confirmation
from .serializers import TransferRequestSerializer, OutSerializer, ConfirmationSerializer

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

from django.http import JsonResponse

from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
import binascii



class TransferRequestView(generics.RetrieveAPIView):
    serializer_class = TransferRequestSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request, *args, **kwargs):
        request.data.update({"user" : request.user.id})
        serializer = TransferRequestSerializer(data=request.data)
        if serializer.is_valid():
            new_transfer = serializer.save()
            if new_transfer:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        request.data.update({"user" : request.user.id})
        if TransferRequest.objects.all().count() == 0:
            return JsonResponse({"transfers": None})
        models = TransferRequest.objects.all()
        related_models = []
        for m in models:
            if request.user in m.related_users:
                related_models.append(m)
        response = []
        for current_model in related_models:
            serialized = TransferRequestSerializer(current_model, context={"request_user" : request.user}).data
            response.append(serialized)
        return JsonResponse({"transfers" : response})


@csrf_exempt
@api_view(["POST"])
def transfer_confirm(request):
    if request.method == 'POST':
        request.data.update({"user" : request.user.id})
        master_password = request.data.get("master_password", None)
        if master_password is None:
            return JsonResponse(status=status.HTTP_403_FORBIDDEN)
        try:
            transfer: TransferRequest = TransferRequest.objects.get(pk=request.data.get("request"))
        except TransferRequest.DoesNotExist:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND)

        if request.user not in transfer.related_users:
            return JsonResponse(status=status.HTTP_403_FORBIDDEN)

        for t in transfer.confirmation_set.all():
            if t.user == request.user:
                return JsonResponse(status=status.HTTP_403_FORBIDDEN)

        serializer = ConfirmationSerializer(data=request.data)
        if serializer.is_valid():
            new_confirmation = transfer.confirmation_set.create(**serializer.validated_data)
            users_private_key = RSA.importKey(extern_key=request.user.account.private_key,
                                              passphrase=request.data.get("master_password"))
            transfer_hash = SHA256.new(int(new_confirmation.code_2fa).to_bytes(4, byteorder="little") + transfer.binary)
            signature = binascii.b2a_hex(pkcs1_15.new(users_private_key).sign(transfer_hash)).decode("UTF-8")
            new_confirmation.signature = signature
            new_confirmation.save()


        if new_confirmation:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
