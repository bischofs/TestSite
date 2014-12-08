from Project.models import Project
from rest_framework import serializers


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
         
        
