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
            data_handler = cache.get(request.session.session_key)
            delay_prep = DelayPrep(data_handler.results_log['Data Alignment'], data_handler.test_data.data, data_handler.master_dict)
            if data_handler.results_log['Data Alignment']['Data'].empty:
                data_handler.results_log['Data Alignment']['Data'] = delay_prep.copy
            js = delay_prep.create_windows()
            cache.set(request.session.session_key, data_handler)

                
            return Response(js,status=200)

        except Exception as e:
            
            return Response({
            'status': 'Bad request',
            'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


    def post(self,request):

        try:

            cache = caches['default']
            data_handler = cache.get(request.session.session_key)

            if request.DATA['delay'] != data_handler.results_log['Data Alignment']['Array']:
                submit = DelaySubmit(data_handler.test_data.data, data_handler.master_dict, request.DATA['delay'], data_handler.cycle_attr['CycleLength'])
                data_handler.test_data.data = submit.data
                data_handler.results_log['Data Alignment']['Array'] = request.DATA['delay']
                data_handler.do_calculation = True

            cache.set(request.session.session_key, data_handler)
                
            return Response(status=200)


        except Exception as e:

            return Response({
            'status': 'Bad request',
            'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

