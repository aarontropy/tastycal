from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.conf import settings


# Import the API
from tastypie.api import Api
from api import CalendarResource, RRuleResource, EventResource
v1_api = Api(api_name='v1')
v1_api.register(CalendarResource())
v1_api.register(EventResource())
v1_api.register(RRuleResource())


urlpatterns = patterns('',
    url(r'^', include(v1_api.urls)),
)

