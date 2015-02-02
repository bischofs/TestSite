from django.shortcuts import render

from Project.serializers import ProjectSerializer
from Project.models import Project
from Authentication.models import Account
from Authentication.serializers import AccountSerializer


from rest_framework import viewsets, status, views
from rest_framework.response import Response

# Create your views here.


class ProjectViewSet(viewsets.ModelViewSet):

    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def list(self, request):
        queryset = Project.objects.all()
        serializer = ProjectSerializer(queryset, many=True)
        return Response(serializer.data)





