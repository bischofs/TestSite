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
            dataHandler = cache.get(request.session._get_session_key())  

            if dataHandler.DoCalculation == True:
                                   
                ##### Initialize Calculation #####
                calculator = Calculator(dataHandler, dataHandler.masterDict, request.QUERY_PARAMS)

                ##### Save Results #####
                dataHandler.resultsLog['Calculation'] = {'ZeroSpan' : calculator.preparation.ZeroSpan.to_json(), 'Fuel' : calculator.preparation.FuelData.to_json(),
                                                        'Array' : calculator.calculation.ArraySum, 'Results' : calculator.calculation.result, 'Data':calculator.calculation.Data}
                dataHandler.DoCalculation = False
            jsonDict = {'Report':dataHandler.resultsLog['Calculation']['Results'][2],'errors': dataHandler.log}
            jsonLog = json.dumps(jsonDict)

            ##### Save Session #####
            cache.set(request.session._get_session_key(), dataHandler)

            return Response(jsonLog, status=200)

        except Exception as e:

            return Response({
            'status': 'Bad request',
            'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, format=None):

        try:
            
            ##### Load dataHandler from Cache #####
            cache = caches['default']
            dataHandler = cache.get(request.session._get_session_key())

            ##### Initialize Report #####
            Output = io.BytesIO()
            report = Report(dataHandler, dataHandler.masterDict, dataHandler.resultsLog['Calculation'], dataHandler.resultsLog['Data Alignment']['Array'], Output)

            ##### Save Session #####
            cache.set(request.session._get_session_key(), dataHandler)

            ##### Prepare the Response #####
            report.output.seek(0)
            Response = HttpResponse(report.output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            Response['Pragma'] = 'public'
            Response['Expires'] = 0
            Response['Cache-Control'] = 'must-revalidate, post-check=0, pre-check=0'
            Response['Cache-Control'] = 'private:false'
            Response['Content-Disposition'] = 'attachment; filename="Final.xlsx"'
            Response['Content-length'] = report.output.tell()

            return Response

        except Exception as e:

            return Response({
            'status': 'Bad request',
            'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
