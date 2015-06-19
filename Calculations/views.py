import json

from django.core.cache import caches
from django.shortcuts import render

from rest_framework import permissions, viewsets, status, views
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.renderers import JSONRenderer

from DataImport.models import DataHandler
from Calculations.models import Calculator
from Calculations.models import Report

class CalculationView(views.APIView):        


        def get(self, request, format=None):

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


        def post(self, request, format=None):
                try:

                    ##### Load dataHandler from Cache #####
                    cache = caches['default']
                    dataHandler = cache.get(request.session._get_session_key())
                    ##### Initialize Calculation #####
                    report = Report(dataHandler)
  
                    jsonDict = {'Report':report,'errors': dataHandler.log}
                    ##### Save Session #####
                    cache.set(request.session._get_session_key(), dataHandler)            
                    #jsonLog = json.dumps(jsonDict)

                    return Response(status=200)

                except Exception as e:

                    return Response({
                    'status': 'Bad request',
                    'message': str(e)
                    }, status=status.HTTP_400_BAD_REQUEST)
