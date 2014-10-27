from django.conf.urls import patterns, include, url
from django.contrib import admin
from TestSite.api import EntryResource

entry_resource = EntryResource()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'TestSite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    (r'^api/', include(entry_resource.urls)),
    url(r'^admin/', include(admin.site.urls)),
)
