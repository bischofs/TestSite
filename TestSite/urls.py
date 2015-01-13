from django.conf.urls import patterns, include, url

from Authentication.views import AccountViewSet, LoginView
from rest_framework import routers
from django.views.generic.base import TemplateView



# Routers provide an easy way of automatically determining the URL conf.
router = routers.SimpleRouter()
router.register(r'accounts', AccountViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.


urlpatterns = patterns('',
        url(r'^api/v1/', include(router.urls)),
        url(r'^api/v1/auth/login/$', LoginView.as_view(), name='login'),
        url(r'^', TemplateView.as_view(template_name='index.html')),
        
        

#url('^.*$', IndexView.as_view(), name='index'),
)
