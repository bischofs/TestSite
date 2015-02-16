from django.shortcuts import render
from rest_framework import permissions, viewsets, status, views
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser

# Create your views here.


class FileUploadView(views.APIView):

    parser_classes = (MultiPartParser,)

    def put(self, request, format=None):

        file_obj = request.FILES['file']
        # ...
        # do some staff with uploaded file
        # ...
        return Response(status=204)





