import json
import io
import xlsxwriter
import os
from django.core.servers.basehttp import FileWrapper

from django.core.cache import caches
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import permissions, viewsets, status, views
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.renderers import JSONRenderer

from DataImport.models import DataHandler
from Calculations.models import Calculator
from Calculations.models import Report
import copy

class CalculationView(views.APIView):


    def post(self, request, format=None):

        try:

            ##### Load dataHandler from Cache #####
            cache = caches['default']
            data_handler = cache.get(request.session._get_session_key())

            if data_handler.do_calculation == True:

                ##### Initialize Calculation #####
                calculator = Calculator(data_handler, data_handler.master_dict, request.QUERY_PARAMS)

                ##### Save Results #####
                data_handler.results_log['Calculation'] = {'ZeroSpan' : calculator.preparation.ZeroSpan.to_json(), 'Fuel' : calculator.preparation.FuelData.to_json(),
                                                        'Array' : calculator.calculation.ArraySum, 'Results' : calculator.calculation.result, 'Data':calculator.calculation.Data}
                data_handler.do_calculation = False
            json_dict = {'Report':data_handler.results_log['Calculation']['Results'][2],'errors': data_handler.log}
            json_log = json.dumps(json_dict)

            ##### Save Session #####
            cache.set(request.session._get_session_key(), data_handler)

            return Response(json_log, status=200)

        except Exception as e:

            return Response({
            'status': 'Bad request',
            'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, format=None):

        try:

            ##### Load dataHandler from Cache #####
            cache = caches['default']
            data_handler = cache.get(request.session.session_key)

            ##### Initialize Report #####
            output = io.BytesIO()
            report = Report(data_handler, data_handler.master_dict, data_handler.results_log['Calculation'], data_handler.results_log['Data Alignment']['Array'], output)

            ##### Save Session #####
            cache.set(request.session.session_key, data_handler)

            ##### Prepare the Response #####
            report.output.seek(0)
            response = HttpResponse(report.output.read(), content_type='application/force-download')
            response['Pragma'] = 'public'
            response['Expires'] = 0
            response['Cache-Control'] = 'must-revalidate, post-check=0, pre-check=0'
            response['Cache-Control'] = 'private:false'
            response['Content-Disposition'] = 'attachment; filename="Final.xlsx"'
            response['Content-length'] = report.output.tell()

            return response

        except Exception as e:

            return Response({
            'status': 'Bad request',
            'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
