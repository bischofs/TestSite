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
                data_handler = DataHandler()
            else:
                data_handler = cache.get(request.session.session_key)

            data_handler.import_data(request.data['file'])
            json_dict = {'errors': data_handler.log, 'CycleAttr': data_handler.cycle_attr,'FilesLoaded':data_handler.all_files_loaded,'File':data_handler.file_type_string}

            cache.set(request.session.session_key, data_handler)
            
            json_log = json.dumps(json_dict)
            return Response(json_log, status=200)
            
        except Exception as e:
         
             return Response({
                 'status': 'Bad request',
                 'message': str(e)
             }, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request):

        try:
            ##### Read in the choice to omit #####
            omit_choice = int(request.QUERY_PARAMS['choice'])

            cache = caches['default']
            data_handler = cache.get(request.session.session_key)

            cycle_validator = CycleValidator(data_handler.test_data, data_handler.master_dict,
                                            data_handler.full_load, data_handler.full_load.meta_data['n_CurbIdle'], omit_choice)

            ##### Saving Results in Log #####
            data_handler.results_log['Regression'] = [cycle_validator.reg_results, cycle_validator.filter_choice]
            data_handler.results_log['Regression_bool'] = cycle_validator.reg_results_bool

            ##### Saving Results in Json-File #####
            json_dict = {'Regression':cycle_validator.reg_results,
                        'Regression_bool':cycle_validator.reg_results_bool,
                        'errors': data_handler.log}
            cache.set(request.session.session_key, data_handler)            
            json_log = json.dumps(json_dict)

            return Response(json_log, status=200)

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
            data_handler = cache.get(request.session.session_key)
            data_handler = None
            cache.set(request.session.session_key, data_handler)
            return Response({'message':'Data cleared!'}, status=200)
        
