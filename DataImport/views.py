import json

from django.core.cache import caches
from django.shortcuts import render
from rest_framework import permissions, viewsets, status, views
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.renderers import JSONRenderer

#from DataImport.models import DataIO
from DataImport.models import CycleValidation, RawDataHandler

# Create your views here.

class FileUploadView(views.APIView):

    parser_classes = (FormParser,MultiPartParser)

    def post(self, request, format=None):
            
        try:
            #if (bool(request.data['cycle'] == ' ')):
            #    raise Exception("Please select a cycle type")
            
            if (bool(request.data['bench'] == ' ')):
                raise Exception("Please select the number of benches used")

            #on first request create RawDataHandler 
            #subsequent requests fill all internal data structs 
            #once all reqs met return container with all required info for delay and math
            #This container will be stored in local server memory ( cache )
            #Each cached file will have a timeout of 10 minutes
            #the final  container will timeout at 8 hours in the cache

            cache = caches['default']
            #this needs to be fixed because the first request will be a file
            #in the current situation it will only save an empty data handler
                
            if(request.data['ftype'] == 'full'):#file is full load curve
                if(not cache.get(request.session._get_session_key())):
                   data_handler = RawDataHandler()
                else:
                   data_handler = cache.get(request.session._get_session_key())
                data_handler.import_full_load(request.data['file'])
                cache.set(request.session._get_session_key(), data_handler)
                jsondict = {'errors': data_handler._log}
            elif(request.data['ftype'] == 'pre'):#file is pre span check
                if(not cache.get(request.session._get_session_key())):
                   data_handler = RawDataHandler()
                else:
                   data_handler = cache.get(request.session._get_session_key())
                data_handler.import_pre_zero_span(request.data['file'])
                cache.set(request.session._get_session_key(), data_handler)
                jsondict = {'errors': data_handler._log}
            elif(request.data['ftype'] == 'post'):#file is post span check 
                if(not cache.get(request.session._get_session_key())):
                   data_handler = RawDataHandler()
                else:
                   data_handler = cache.get(request.session._get_session_key())
                data_handler.import_post_zero_span(request.data['file'])
                cache.set(request.session._get_session_key(), data_handler)
                jsondict = {'errors': data_handler._log}
            elif(request.data['ftype'] == 'test'):#file is test data
                if(not cache.get(request.session._get_session_key())):
                   data_handler = RawDataHandler()
                else:
                   data_handler = cache.get(request.session._get_session_key())
                data_handler._import_test_data(request.data['bench'],request.data['file'])
                cache.set(request.session._get_session_key(), data_handler)
                data_valid = CycleValidation(data_handler.testData, data_handler.mapDict)
                reg_results = data_valid.reg_results
                jsondict = {'regression':reg_results, 'errors': data_handler._log}
                

                

            #if first request 
             # create rawdatahandlder
             # import whatever file that is in the request
             # save raw data to cache
            #import pdb; pdb.set_trace()

            jsonLog = json.dumps(jsondict)
            return Response(jsonLog, status=200)
            
        except Exception as e:

            return Response({
                'status': 'Bad request',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)



class MetaDataView(views.APIView):

    
    def get(self, request, *args, **kwargs):
        import pdb; pdb.set_trace()

        return HttpResponse('Hello, World!')
