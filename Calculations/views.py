import json
import xlsxwriter
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

class CalculationView(views.APIView):        


        def post(self, request, format=None):

                try:

                    ##### Load dataHandler from Cache #####
                    cache = caches['default']
                    dataHandler = cache.get(request.session._get_session_key())
                    ##### Initialize Calculation #####
                    calculator = Calculator(dataHandler, dataHandler.testDataMapDict, request.QUERY_PARAMS)
                    ##### Save Results #####
                    dataHandler.resultsLog['Calculation'] = calculator
                    #jsonDict = {'Calculation':calculator,'errors': dataHandler.log}
                    ##### Save Session #####
                    cache.set(request.session._get_session_key(), dataHandler)            
                    #jsonLog = json.dumps(jsonDict)

                    return Response(status=200)

                except Exception as e:

                    return Response({
                    'status': 'Bad request',
                    'message': str(e)
                    }, status=status.HTTP_400_BAD_REQUEST)


        def get(self, request, format=None):

                try:

                    import ipdb
                    ipdb.set_trace()

                    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    response['Content-Disposition'] = 'attachment; filename=Final.xlsx'

                    ##### Load dataHandler from Cache #####
                    cache = caches['default']
                    dataHandler = cache.get(request.session._get_session_key())
                    ##### Initialize Calculation #####
                    #fileReport = xlsxwriter.Workbook(response)
                    report = Report(dataHandler)


                    #wrapper = FileWrapper(fileReport)
                    response = HttpResponse(report.file)
                    #response['Content-Length'] = os.path.getsize(filename)
                    #return response
  
                    #jsonDict = {'Report':report,'errors': dataHandler.log}
                    ##### Save Session #####
                    cache.set(request.session._get_session_key(), dataHandler)            
                    #jsonLog = json.dumps(jsonDict)

                    return response

                except Exception as e:

                    return Response({
                    'status': 'Bad request',
                    'message': str(e)
                    }, status=status.HTTP_400_BAD_REQUEST)
