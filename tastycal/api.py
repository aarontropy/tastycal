from tastypie.resources import ModelResource, ALL_WITH_RELATIONS, ALL
from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.authorization import DjangoAuthorization
from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import json
import pytz
from datetime import datetime

from models import Calendar, Event, RRule



#===============================================================================
class EventResource(ModelResource):
    calendar = fields.ForeignKey('tastycal.api.CalendarResource', 'calendar')
    rule = fields.ForeignKey('tastycal.api.RRuleResource', 'rule', null=True)

    #===========================================================================
    class Meta:
        queryset = Event.objects.all()
        resource_name = 'event'
        collection_name = 'events'
        authorization = DjangoAuthorization()
        filtering = {
            'calendar': ALL_WITH_RELATIONS,
            'start': ALL,
            'end': ALL,
        }

    def build_filters(self, filters=None): 
        '''
        Currently, some clients (OK, arshaw's FullCalendar) send time 
        ranges as timestamps.  tastypie reuires ISO-8601 format 
        out-of-the-box.
        FullCalendar may soon change the way it sends time ranges
        (see https://gist.github.com/arshaw/6420506), but until then,
        we have to do the work ourselves.

        '''
        if filters is None: 
            filters = {} 

        orm_filters = super(EventResource, self).build_filters(filters) 
        if 'start__gte' in orm_filters and orm_filters['start__gte'].isnumeric(): 
            orm_filters['start__gte'] = pytz.UTC.localize(datetime.utcfromtimestamp(float(orm_filters['start__gte'])) )
        if 'start__lte' in orm_filters and orm_filters['start__lte'].isnumeric(): 
            orm_filters['start__lte'] = pytz.UTC.localize(datetime.utcfromtimestamp(float(orm_filters['start__lte'])) )

        return orm_filters 


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
        filtering = {
            'id': ALL,
        }

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w+)/events%s$" % (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('dispatch_event_list'), 
                name="api_dispatch_event_list"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w+)/rules%s$" % (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('dispatch_rule_list'), 
                name="api_dispatch_rule_list"),
        ]

    def dispatch_event_list(self, request, **kwargs):
        event_resource = EventResource()
        kwargs['calendar__id'] = kwargs.pop('pk')
        return event_resource.dispatch('list', request, **kwargs)

    def dispatch_rule_list(self, request, **kwargs):
        rule_resource = RRuleResource()
        kwargs['calendar__id'] = kwargs.pop('pk')
        return rule_resource.dispatch('list', request, **kwargs)

    def dehydrate(self, bundle):
        bundle.data['events_uri'] = self._build_reverse_url('api_dispatch_event_list', 
            kwargs=self.resource_uri_kwargs(bundle))
        bundle.data['rules_uri'] = self._build_reverse_url('api_dispatch_rule_list', 
            kwargs=self.resource_uri_kwargs(bundle))
        return bundle





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
