import json

from django.shortcuts import render
from rest_framework import permissions, viewsets, status, views
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.renderers import JSONRenderer

from DataImport.models import DataIO

# Create your views here.

class FileUploadView(views.APIView):

    parser_classes = (MultiPartParser,)

    def put(self, request, format=None):

        file_obj = request.FILES['file']
        cycle_type = request.DATA

        try:

            data = DataIO()
            data.load_data(file_obj)
            jsonLog = json.dumps(data.logDict)
            return Response(jsonLog, status=200)

        except Exception as e:
             # import pdb; pdb.set_trace()

             return Response({
                'status': 'Bad request',
                'message': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)





