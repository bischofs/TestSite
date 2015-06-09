from django.shortcuts import render
from django.core.cache import caches

from rest_framework import permissions, viewsets, status, views
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.renderers import JSONRenderer

from Delay.models import DelayPrep

# Create your views here.

class DelayView(views.APIView):


    def get(self, request, format=None):

        cache = caches['default']

        if(not cache.get(request.session._get_session_key())):
            return Response(status=400)
        else:
            dataHandler = cache.get(request.session._get_session_key())
            delayPrep = DelayPrep(dataHandler.testData.data, dataHandler.testDataMapDict, True)
            js = delayPrep.create_windows()
            #if(dataHandler.allFilesUploaded == False):
                
        return Response(js,status=200)




    #def post(self)  post delays
