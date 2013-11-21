from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin

from demo import views

from tastycal import urls as tastyurls

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', views.index, name='home'),
    url(r'^jquery/(\d+)/$', views.jquery_view, name='jquery_view'),
    url(r'^api/', include(tastyurls)),


    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
