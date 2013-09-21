from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin

from demo import views

from tastycal import urls as tastyurls

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),
    url(r'^jquery/$', views.jquery_view, name='jquery_view'),
    url(r'^cal/', include(tastyurls)),
    # url(r'^demo/', include('demo.foo.urls')),


    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
