from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, AccountSerializer, GroupSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User, Group, GroupManager
from rest_framework import generics
from.models import Account
from Crypto.PublicKey import RSA
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from transfers.tasks import worker_is_running


class WorkerAPI(APIView):
    def post(self, request, format='json'):
        worker_group = Group.objects.get(name = "worker")
        worker = User.objects.filter(groups__name__contains = worker_group.name)
        master_password = request.data.get("master_password", None)
        if worker.count() == 0 and master_password is not None:
            worker_object = User.objects.create(username="worker", password="workerpwd")
            worker_object.groups.add(worker_group)
            worker_object.save()
            key = RSA.generate(bits=2048)
            private_key = key.exportKey(format="PEM",passphrase=master_password).decode("UTF-8")
            public_key = key.publickey().exportKey(format="PEM").decode("UTF-8")
            worker_account_object = Account.objects.create(user=worker_object, private_key=private_key, public_key=public_key)
            worker_account_object.save()

        return Response(status=status.HTTP_200_OK)
    def get(self, request, format='json'):
        worker_group = Group.objects.get(name = "worker")
        worker = User.objects.filter(groups__name__contains = worker_group.name)
        worker_created = False
        if worker.count() == 1:
            worker_created = True
        return Response({"worker": {"created": worker_created, "started": False}}, status=status.HTTP_200_OK)



class UserAPI(APIView):
    permission_classes = ()
    authentication_classes = (TokenAuthentication,)

    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format='json'):
        user_object = User.objects.get( pk=request.data.get("id") )
        User.delete(user_object)
        return Response(status=status.HTTP_200_OK)

class GroupsAPI(APIView):
    groups = [{"name" : "owner"}, {"name" : "manager"}, {"name" : "worker"}, {"name" : "fetcher"}, {"name" : "collector"}]

    def post(self, request, format='json'):
        for g in self.groups:
            Group.objects.get_or_create(name=g["name"])


        return Response(status=status.HTTP_200_OK)


class UserList(APIView):
    def get(self, request, format='json'):
        user_objects = User.objects.all()
        serializer = UserSerializer(user_objects, many=True, read_only=True)
        group_objects = Group.objects.all()
        groups_serializer = GroupSerializer(group_objects, many=True, read_only=True)

        return Response({"users" : serializer.data, "groups" : groups_serializer.data}, status=status.HTTP_200_OK)


class AccountCreate(generics.RetrieveAPIView):
    serializer_class = AccountSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request, format='json'):
        request.data.update({"user" : request.user.id})
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            new_account = serializer.save()

            rsa_impl = RSA
            if not new_account.private_key:
                key = rsa_impl.generate(bits=2048)
                new_account.private_key = key.exportKey(format="PEM",
                                                    passphrase=request.data.get("master_password", "default")).decode("UTF-8")
                new_account.public_key = key.publickey().exportKey(format="PEM").decode("UTF-8")
                new_account.save()

            if new_account:
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format="json"):
        request.data.update({"user" : request.user.id})
        if Account.objects.all().count() == 0:
            return JsonResponse({"account": None})
        account = Account.objects.filter(user=request.user.id).first()
        account_serialized = AccountSerializer(account).data
        return JsonResponse({"account" : account_serialized})

@csrf_exempt
def accounts_list(request):
    if request.method == 'GET':
        user_id = request.user.id

        models = Account.objects.all()
        response = {}
        for current_model in models:
            serialized = AccountSerializer(current_model).data
            response[current_model.id] = serialized
        return JsonResponse({"accounts" : response})
