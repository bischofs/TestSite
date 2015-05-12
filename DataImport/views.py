
import json

from django.core.cache import caches
from django.shortcuts import render

from rest_framework import permissions, viewsets, status, views
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.renderers import JSONRenderer

from DataImport.models import CycleValidator, RawDataHandler

class FileUploadView(views.APIView):

    #on first request create RawDataHandler 
    #subsequent requests fill all internal data structs 
    #once all reqs met return container with all required info for delay and math
    #This container will be stored in local server memory ( cache )
    #Each cached file will have a timeout of 10 minutes
    #the final  container will timeout at 8 hours in the cache


    parser_classes = (FormParser,MultiPartParser)

    def post(self, request, format=None):
            
        try:

            if (bool(request.data['bench'] == ' ')):
                raise Exception("Please select the number of benches used")

            cache = caches['default']

            if(not cache.get(request.session._get_session_key())):
                dataHandler = RawDataHandler()
            else:
                dataHandler = cache.get(request.session._get_session_key())

            if(request.data['ftype'] == 'full'):#file is full load curve
                dataHandler.import_full_load(request.data['file'])
                jsonDict = {'errors': dataHandler.log}
            elif(request.data['ftype'] == 'pre'):#file is pre span check
                dataHandler.import_pre_zero_span(request.data['file'])
                jsonDict = {'errors': dataHandler.log}
            elif(request.data['ftype'] == 'post'):#file is post span check 
                dataHandler.import_post_zero_span(request.data['file'])
                jsonDict = {'errors': dataHandler.log}
            elif(request.data['ftype'] == 'test'):#file is test data
                dataHandler.import_test_data(request.data['bench'], request.data['file'])
                dataValid = CycleValidator(dataHandler.testData, dataHandler.mapDict)
                regResults = dataValid.reg_results
                jsonDict = {'regression':regResults, 'errors': dataHandler.log}

            cache.set(request.session._get_session_key(), dataHandler)
                
            jsonLog = json.dumps(jsonDict)
            return Response(jsonLog, status=200)
            
        except Exception as e:

            return Response({
                'status': 'Bad request',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)



class MetaDataView(views.APIView):

    
    def get(self, request, *args, **kwargs):


        return HttpResponse('Hello, World!')
