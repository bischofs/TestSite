from django.shortcuts import render
from django.core.cache import caches

from rest_framework import permissions, viewsets, status, views
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.renderers import JSONRenderer

from Delay.models import DelayPrep
from Delay.models import DelaySubmit

# Create your views here.

class DelayView(views.APIView):

    def get(self, request, format=None):

        try:

            cache = caches['default']
            dataHandler = cache.get(request.session.session_key)

            delayPrep = DelayPrep(dataHandler.testData.data, dataHandler.masterDict, dataHandler.CoHigh)
            js = delayPrep.create_windows()
            #if(dataHandler.allFilesUploaded == False):
                
            return Response(js,status=200)

        except Exception as e:

            return Response({
            'status': 'Bad request',
            'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


    def post(self,request):

        try:

            cache = caches['default']
            dataHandler = cache.get(request.session.session_key)

            Submit = DelaySubmit(dataHandler.testData.data, dataHandler.masterDict, request.DATA['delay'], dataHandler.CoHigh)
            dataHandler.testData.data = Submit.Data
            dataHandler.resultsLog['Data Alignment'] = Submit.Array

            cache.set(request.session.session_key, dataHandler)
                
            return Response(status=200)


        except Exception as e:

            return Response({
            'status': 'Bad request',
            'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)





    #def post(self)  post delays
