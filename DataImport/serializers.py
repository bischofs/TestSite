
from DataImport.models import DataIO
from rest_framework import serializers

class DataIOSerializer(serializers.ModelSerializer):

    logDict = serializers.DictField()

    class Meta:

        model = DataIO
        fields = ('logDict',)