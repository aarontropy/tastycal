from django.conf.urls import patterns, include, url
from django.contrib import admin
from tastycal import urls as tastyurls

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^cal/', include(tastyurls)),
    # url(r'^demo/', include('demo.foo.urls')),


    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
