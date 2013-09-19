from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.authorization import DjangoAuthorization
from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import json

from models import Calendar, Event, RRule



#===============================================================================
class EventResource(ModelResource):

    #===========================================================================
    class Meta:
        queryset = Event.objects.all()
        resource_name = 'event'
        collection_name = 'events'
        authorization = DjangoAuthorization()

#===============================================================================
class RRuleResource(ModelResource):
    events = fields.ToManyField(EventResource, 'events')

    #===========================================================================
    class Meta:
        queryset = RRule.objects.all()
        resource_name = 'rrule'
        collection_name = 'rrules'
        authorization = DjangoAuthorization()



#===============================================================================
class CalendarResource(ModelResource):
    events = fields.ToManyField(EventResource, 'events')

    #===========================================================================
    class Meta:
        queryset = Calendar.objects.all()
        resource_name = 'calendar'
        collection_name = 'calendars'
        authorization = DjangoAuthorization()





# class OccurrenceResource(ModelResource):
#     event = fields.ForeignKey('swapi.api.EventResource', 'event')
#     class Meta:
#         queryset = Occurrence.objects.all()
#         resource_name = 'occurrence'
#         collection_name = 'events'
#         authorization = DjangoAuthorization()


#     def dehydrate(self, bundle):
#         bundle.data['title'] = bundle.obj.event.title
#         bundle.data['start'] = bundle.data.pop('start_time')
#         bundle.data['end'] = bundle.data.pop('end_time')
#         return bundle


 


# class EventResource(ModelResource):
#     occurrences = fields.ToManyField(OccurrenceResource, 'occurrence_set')

#     class Meta:
#         queryset = Event.objects.all()
#         resource_name = 'event'


#     def prepend_urls(self):
#         return [
#             ### OCCURRENCES FOR THIS EVENT
#             url(r"^(?P<resource_name>%s)/(?P<pk>\w+)/occurrences%s$" % (self._meta.resource_name, trailing_slash()), 
#                 self.wrap_view('get_occurrences'), 
#                 name="api_dispatch_detail_occurrences"),
#         ]

#     def get_occurrences(self, request, **kwargs):
#         try:
#             bundle = self.build_bundle(data={'pk': kwargs['pk']}, request=request)
#             event = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
#         except ObjectDoesNotExist:
#             return HttpGone()
#         except MultipleObjectsReturned:
#             return HttpMultipleChoices("More than one resource is found at this URI.")

#         occurrence_resource = OccurrenceResource()
#         return occurrence_resource.get_list(request, event_id=event.id) 
