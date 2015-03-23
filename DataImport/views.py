import json

from django.core.cache import caches
from django.shortcuts import render
from rest_framework import permissions, viewsets, status, views
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.renderers import JSONRenderer



from DataImport.models import DataIO
from DataImport.models import CycleValidation

# Create your views here.

class FileUploadView(views.APIView):

    parser_classes = (FormParser,MultiPartParser)

    def post(self, request, format=None):
    
        
        try:
            if (bool(request.data['cycle'] == ' ')):
                raise Exception("Please select a cycle type")
            
            if (bool(request.data['bench'] == ' ')):
                raise Exception("Please select the number of benches used")
            
            data_io = DataIO(request.data['cycle'], request.data['bench'])
            raw_data, map_dict, log_dict = data_io.load_data(request.data['file'])
            
            data_valid = CycleValidation(raw_data, map_dict)
            
            reg_results = data_valid.reg_results

            # cache = caches['default']
            # cache.set(request.session._get_session_key, data)


            jsondict = {'regression':reg_results, 'errors': log_dict}

            jsonLog = json.dumps(jsondict)
            


            return Response(jsonLog, status=200)
            
        except Exception as e:
            
            return Response({
                'status': 'Bad request',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)






        # if (bool(request.data['cycle'] == ' ')):
        #     raise Exception("Please select a cycle type")
                
        # if (bool(request.data['bench'] == ' ')):
        #     raise Exception("Please select the number of benches used")
                
        # data_io = DataIO(request.data['cycle'], request.data['bench'])
        # raw_data, map_dict, log_dict = data_io.load_data(request.data['file'])
        
        # data_valid = CycleValidation(raw_data, map_dict)
        # data_valid.regression() 

            
        # # cache = caches['default']
        # # cache.set(request.session._get_session_key, data)

        # jsonLog = json.dumps(log_dict)
            

        # return Response(jsonLog, status=200)


