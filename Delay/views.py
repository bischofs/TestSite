from django.shortcuts import render
from django.core.cache import caches

from rest_framework import permissions, viewsets, status, views
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.renderers import JSONRenderer

# Create your views here.

class DelayView(views.APIView):


    def get(self, request, format=None):

        cache = caches['default']

        if(not cache.get(request.session._get_session_key())):
            return Response(status=400)
        else:
            dataHandler = cache.get(request.session._get_session_key())
            #if(dataHandler.allFilesUploaded == False):
                
        import ipdb; ipdb.set_trace()                    
                
        return Response(status=200)




    #def post(self)  post delays
