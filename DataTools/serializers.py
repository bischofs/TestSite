from django.contrib.auth.models import User, Group
from rest_framework import serializers
from DataTools.models import UserProfile
from django.http  import HttpResponse as request

#class UserSerializer(serializers.HyperlinkedModelSerializer):
#    class Meta:
#        model = User
#        fields = ('url', 'username', 'email', 'groups')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    #posts = serializers.HyperlinkedIdentityField('posts', view_name='userpost-list', lookup_field='username')


    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff' )
        context={'request': request}



