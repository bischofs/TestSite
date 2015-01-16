from Project.models import Project
from rest_framework import serializers


class ProjectSerializer(serializers.ModelSerializer):

  accounts = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='title'
     )

    class Meta:
        model = Project
        fields = ('id', 'name', 'accounts')
        
