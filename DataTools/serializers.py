from django.contrib.auth.models import User, Group
from rest_framework import serializers
from DataTools.models import UserProfile
from django.http  import HttpResponse as request

#class UserSerializer(serializers.HyperlinkedModelSerializer):
#    class Meta:
#        model = User
#        fields = ('url', 'username', 'email', 'groups')




