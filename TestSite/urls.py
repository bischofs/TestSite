from django.conf.urls import patterns, include, url
from django.conf import settings

from Project.views import ProjectViewSet
from Authentication.views import AccountViewSet, LoginView, LogoutView
from DataImport.views import FileUploadView, MetaDataView
from Calculations.views import CalculationView
from Delay.views import DelayView
from rest_framework import routers

from django.views.generic.base import TemplateView
from django.contrib import admin
admin.autodiscover()


# Routers provide an easy way of automatically determining the URL conf.
router = routers.SimpleRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'projects', ProjectViewSet)
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.


urlpatterns = patterns('',
        url(r'^1065/api/v1/', include(router.urls)),
        url(r'^1065/admin/', include(admin.site.urls)),
        url(r'^1065/api/v1/auth/login/$', LoginView.as_view(), name='login'),
        url(r'^1065/api/v1/auth/logout/$', LogoutView.as_view(), name='logout'),
        url(r'^1065/api/v1/data/import/$', FileUploadView.as_view(), name='upload'),
        url(r'^1065/api/v1/data/meta/$', MetaDataView.as_view(), name='meta'),
        url(r'^1065/api/v1/data/delay/$',DelayView.as_view(), name='delay'),
        url(r'^1065/api/v1/data/calculations/$',CalculationView.as_view(), name='calc'),
        url(r'^1065/static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, 'show_indexes': settings.DEBUG}),
        url(r'^1065/', TemplateView.as_view(template_name='index.html')), #I THINK THIS ALWAYS HAS TO BE THE LAST ONE


#url('^.*$', IndexView.as_view(), name='index'),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
