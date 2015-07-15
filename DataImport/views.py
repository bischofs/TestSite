
import json

from django.core.cache import caches
from django.shortcuts import render

from rest_framework import permissions, viewsets, status, views
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.renderers import JSONRenderer

from DataImport.models import CycleValidator, DataHandler

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
            
            cache = caches['default']

            request.session.set_test_cookie()

            if(not cache.get(request.session.session_key)):
                dataHandler = DataHandler()
            else:
                dataHandler = cache.get(request.session.session_key)

            dataHandler.import_data(request.data['file'])
            jsonDict = {'errors': dataHandler.log, 'CycleAttr': dataHandler.CycleAttr,'FilesLoaded':dataHandler.allFilesLoaded,'File':dataHandler.File}

            cache.set(request.session.session_key, dataHandler)
            
            jsonLog = json.dumps(jsonDict)
            return Response(jsonLog, status=200)
            
        except Exception as e:
         
             return Response({
                 'status': 'Bad request',
                 'message': str(e)
             }, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request):

        try:
            
            ##### Read in the choice to omit #####
            OmitChoice = int(request.QUERY_PARAMS['choice'])

            cache = caches['default']
            dataHandler = cache.get(request.session.session_key)

            cycleValidator = CycleValidator(dataHandler.testData, dataHandler.masterDict,
                                            dataHandler.fullLoad, dataHandler.fullLoad.metaData['n_CurbIdle'], OmitChoice)

            ##### Saving Results in Log #####
            dataHandler.resultsLog['Regression'] = [cycleValidator.reg_results,cycleValidator.FilterChoice]
            dataHandler.resultsLog['Regression_bool'] = cycleValidator.reg_results_bool      

            ##### Saving Results in Json-File #####
            jsonDict = {'Regression':cycleValidator.reg_results,
                        'Regression_bool':cycleValidator.reg_results_bool,
                        'errors': dataHandler.log}
            cache.set(request.session.session_key, dataHandler)            
            jsonLog = json.dumps(jsonDict)

            return Response(jsonLog, status=200)

        except Exception as e:        
        
            return Response({
            'status': 'Bad request',
            'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class MetaDataView(views.APIView):

    
    def get(self, request):

        cache = caches['default']

        request.session.set_test_cookie()

        if(not cache.get(request.session.session_key)):
            return Response({'message':'No Data available!'}, status=200) 
        else:
            dataHandler = cache.get(request.session.session_key)
            dataHandler = None
            cache.set(request.session.session_key, dataHandler)
            return Response({'message':'Data cleared!'}, status=200)
        
