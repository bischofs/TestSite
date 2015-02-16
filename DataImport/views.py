from django.shortcuts import render
from rest_framework import permissions, viewsets, status, views
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser

from DataImport.models import DataIO

# Create your views here.


class FileUploadView(views.APIView):

    parser_classes = (MultiPartParser,)

    def put(self, request, format=None):

        file_obj = request.FILES['file']

        data = DataIO()

        try:
            data.load_data(file_obj)
            return Response(status=204)
        except Exception as e:
            return Response({
                'status': 'Bad request',
                'message': str(e)
             }, status=status.HTTP_400_BAD_REQUEST)





