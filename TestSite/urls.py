from django.conf.urls import patterns, include, url
from django.conf import settings

from Project.views import ProjectViewSet
from Authentication.views import AccountViewSet, LoginView, LogoutView
from DataImport.views import FileUploadView
from rest_framework import routers

from django.views.generic.base import TemplateView



# Routers provide an easy way of automatically determining the URL conf.
router = routers.SimpleRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'projects', ProjectViewSet)
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.


urlpatterns = patterns('',
        url(r'^api/v1/', include(router.urls)),
        url(r'^api/v1/auth/login/$', LoginView.as_view(), name='login'),
        url(r'^api/v1/auth/logout/$', LogoutView.as_view(), name='logout'),
        url(r'^', TemplateView.as_view(template_name='index.html')),
        url(r'^api/v1/data/import/', FileUploadView.as_view()),

#url('^.*$', IndexView.as_view(), name='index'),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
