from django.shortcuts import render

# Create your views here.
from rest_framework import permissions, viewsets

from Authentication.models import Account
from Authentication.permissions import IsAccountOwner
from Authentication.serializers import AccountSerializer



class AccountViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'
    queryset = Account.objects.all()
    serializer_class = AccountSerializer



    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.AllowAny(),)

        if self.request.method == 'POST':
            return (permissions.AllowAny(),)

        return (permissions.IsAuthenticated(), IsAccountOwner(),)



    def create(self, request):
        serializer = self.serializer_class(data=request.DATA)

        if serializer.is_valid():
            account = Account.objects.create_user(**request.DATA)

            account.set_password(request.DATA.get('password'))
            account.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({
            'status': 'Bad request',
            'message': 'Account could not be created with received data.'
        }, status=status.HTTP_400_BAD_REQUEST)