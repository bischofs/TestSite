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
    context={'request': request}    


    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff' )


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', required=False)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)

    class Meta:
        model = UserProfile
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'tagline',
            'created_at', 'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at',)

    def restore_object(self, attrs, instance=None):
        profile = super(UserProfileSerializer, self).restore_object(
            attrs, instance
        )

        if profile:
            user = profile.user

            user.email = attrs.get('user.email', user.email)
            user.first_name = attrs.get('user.first_name', user.first_name)
            user.last_name = attrs.get('user.last_name', user.last_name)

            user.save()

        return profile
