from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.db.models import Q
from .models import PrivateKey
from .serializers import PrivateKeySerializer
from .permissions import IsOwnerOrReadOnly
from django.contrib.auth.models import User
from rest_framework import mixins
from rest_framework import generics
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from address.models import Address
from address.serializers import AddressSerializer
from rest_framework.decorators import api_view
from accounts.models import Account
from firewall.models import FirewallAddress

from rest_framework.response import Response
from rest_framework import status
import bitcoin
import binascii
from cryptoassets.factory.currency_model_factory import CurrencyModelFactory


# Create your views here.
@csrf_exempt
def keys_list(request):
    if request.method == 'GET':
        keys = PrivateKey.objects.all()
        serializer = PrivateKeySerializer(keys, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = PrivateKeySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

@csrf_exempt
def key_details(request, pk):
    try:
        privatekey = PrivateKey.objects.get(pk=pk)
    except PrivateKey.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = PrivateKeySerializer(privatekey)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = PrivateKeySerializer(privatekey, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        privatekey.delete()
        return HttpResponse(status=204)

class KeyDetails(generics.RetrieveAPIView):
    serializer_class = PrivateKeySerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )

    @csrf_exempt
    def post(self, request, format='json'):
        request.data.update({"owner" : request.user.id})
        serializer = PrivateKeySerializer(data=request.data)


        if serializer.is_valid():
            new_key = serializer.save()


            if not new_key.private_key:
                if new_key.private_key_type == PrivateKey.KEY_TYPE_SEED:
                    new_key_data = bitcoin.random_key()
                    users_public_key = RSA.importKey(extern_key=new_key.owner.account.public_key)
                    new_key.private_key = binascii.b2a_hex(PKCS1_OAEP.new(users_public_key).encrypt(new_key_data.encode("UTF-8"))).decode("UTF-8")
                    new_key.save()

                if new_key.private_key_type == PrivateKey.KEY_TYPE_ROOT:
                    users_private_key = RSA.importKey(extern_key=new_key.owner.account.private_key, passphrase=request.data.get("master_password"))
                    seed = PKCS1_OAEP.new(users_private_key).decrypt( binascii.a2b_hex(new_key.parent_key.private_key)).decode("UTF-8")
                    currency_factory = CurrencyModelFactory()
                    currency_model = currency_factory.get_currency_model(new_key.asset.symbol, new_key.network_type)
                    public_key = currency_model.generate_xpub(binascii.a2b_hex(seed))
                    private_key = currency_model.generate_xpriv(binascii.a2b_hex(seed))
                    new_key.private_key = binascii.b2a_hex(PKCS1_OAEP.new(users_private_key).encrypt(private_key.encode("UTF-8"))).decode("UTF-8")
                    new_key.public_key = public_key
                    new_key.save()

            if new_key:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        key_type_choices = PrivateKey._meta.get_field('private_key_type').choices
        network_type_choices = PrivateKey._meta.get_field('network_type').choices

        serializer = PrivateKeySerializer(data=request.data)

        if PrivateKey.objects.filter(Q(owner=request.user) | Q(shared_keys=request.user)).distinct().count() == 0:
            return JsonResponse({"keys": None, "key_types" : key_type_choices, "network_types" : network_type_choices})

        models = PrivateKey.objects.filter(Q(owner=request.user) | Q(shared_keys=request.user)).distinct()
        response = {}
        for current_model in models:
            serialized = PrivateKeySerializer(current_model).data
            response[current_model.id] = serialized
        return JsonResponse({"keys" : response, "key_types" : key_type_choices, "network_types" : network_type_choices})



@csrf_exempt
def key_address(request, pk, n):
    try:
        privatekey: PrivateKey = PrivateKey.objects.get(pk=pk)
    except PrivateKey.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'POST':
        currency_factory = CurrencyModelFactory()
        currency_model = currency_factory.get_currency_model(privatekey.asset.symbol, privatekey.network_type)
        address = currency_model.get_addr_from_pub(privatekey.public_key, n)
        address_model = Address.objects.filter(private_key=privatekey, address=address).first()
        if not address_model:
            address_model = Address(private_key=privatekey, address=address, n=n)
            address_model.save()
        return JsonResponse({"address" : address})

@csrf_exempt
def key_addresses(request, pk):
    try:
        privatekey: PrivateKey = PrivateKey.objects.get(pk=pk)
    except PrivateKey.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        user_id = request.user.id
        if PrivateKey.objects.filter(owner=user_id, id=pk).count() == 0:
            return JsonResponse({"address": None})


        models = Address.objects.filter(private_key=pk)
        response = {}
        for current_model in models:
            serialized = AddressSerializer(current_model).data
            response[current_model.n] = serialized
        return JsonResponse({"address" : response})

@csrf_exempt
@api_view(["GET"])
def address_validate(request, address):
    firewall_addresses = FirewallAddress.objects.filter(address=address)
    if firewall_addresses.count() == 0:
        return JsonResponse({address: 0})
    return JsonResponse({address: 1})


@csrf_exempt
@api_view(["POST"])
def key_share(request):
    if request.method == 'POST':
        try:
            privatekey: PrivateKey = PrivateKey.objects.get(pk=request.data.get("id"))
        except PrivateKey.DoesNotExist:
            return JsonResponse(status=404)

        if privatekey.owner != request.user:
            return JsonResponse(status=status.HTTP_401_UNAUTHORIZED)

        user_id = request.user.id
        share_to = request.data.get("share_to",[])
        already_shared_to = []

        for s in privatekey.shared_keys.all():
            if s.id not in share_to:
                s.delete()
            else:
                already_shared_to.append(s.id)

        users_private_key = RSA.importKey(extern_key=privatekey.owner.account.private_key,
                                          passphrase=request.data.get("master_password"))
        decoded_key = PKCS1_OAEP.new(users_private_key).decrypt(binascii.a2b_hex(privatekey.parent_key.private_key)).decode(
            "UTF-8")

        shared_with = []

        for current_user_id in share_to:
            if current_user_id in already_shared_to:
                continue
            new_owner = User.objects.get(pk=current_user_id)
            if new_owner is None or new_owner.account.public_key is None:
                continue
            if new_owner.username == "Worker":
                new_owner_public_key = RSA.importKey(extern_key=new_owner.account.public_key)

                encoded_private_key = binascii.b2a_hex(
                    PKCS1_OAEP.new(new_owner_public_key).encrypt(decoded_key.encode("UTF-8"))).decode("UTF-8")

                new_key = PrivateKey(name=privatekey.name + "_shared",  owner=new_owner, parent_key=privatekey, private_key=encoded_private_key, public_key=privatekey.public_key,
                                     private_key_type=privatekey.private_key_type, asset=privatekey.asset, network_type=privatekey.network_type)
                new_key.save()
            shared_with.append(current_user_id)
            privatekey.shared_keys.add(new_owner)
            privatekey.save()
        return JsonResponse({"shared" : shared_with})



'''
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)




class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
'''