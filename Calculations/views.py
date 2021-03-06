import json

from django.core.cache import caches
from django.shortcuts import render

from rest_framework import permissions, viewsets, status, views
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.renderers import JSONRenderer

from DataImport.models import DataHandler

class CalculationView(views.APIView):

	def post(self, request, format=None):

		try:

			##### Load dataHandler from Cache #####
			cache = caches['default']
                  dataHandler = cache.get(request.session._get_session_key())

                  ##### Initialize Calculation #####
                  calculator = Calculator(dataHandler, dataHandler.testDataMapDict, request.QUERY_PARAMS)

                  ##### Save Results #####
                  dataHandler.resultsLog['Calculation'] = calculator.report
                  jsonDict = {'Calculation':calculator.reg_results,'errors': dataHandler.log}

                  ##### Save Session #####
                  cache.set(request.session._get_session_key(), dataHandler)            
                  jsonLog = json.dumps(jsonDict)
                  return Response(jsonLog, status=200)

      	except Exception, e:

      		return Response({
      			'status': 'Bad request',
      			'message': str(e)
      			}, status=status.HTTP_400_BAD_REQUEST)

