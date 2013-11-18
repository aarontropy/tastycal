from tastypie.resources import ModelResource, ALL_WITH_RELATIONS, ALL
from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.authentication import Authentication
from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import json
import pytz
from datetime import datetime
from dateutil.parser import parse

from models import Calendar, Event, RRule

#TODO:
# 1. Separate RRule resource from Event Resource

#===============================================================================
class EventResource(ModelResource):
    """
    The API will abstract
    away the difference between an event and a recurring event.  Clients will
    set event details and recurrence by PUT/POST/PATCH to the same resource.
    Creating RRule or Event objects will be handled behind the scene.

    """
    calendar = fields.ForeignKey('tastycal.api.CalendarResource', 'calendar')
    rule = fields.ForeignKey('tastycal.api.RRuleResource', 'rule', null=True, full=True)

    #===========================================================================
    class Meta:
        allowed_methods = ['get', 'post', 'put', 'patch', 'delete']
        queryset = Event.objects.all()
        resource_name = 'event'
        collection_name = 'events'
        authorization = Authorization()
        authentication = Authentication()
        filtering = {
            'calendar': ALL_WITH_RELATIONS,
            'start': ALL,
            'end': ALL,
        }


    def alter_deserialized_detail_data(self, request, data):
        if getattr(self, 'parent_calendar', None):
            data['calendar'] = self.parent_calendar
        return data

    def dehydrate(self, bundle):
        # Add a repeat flag, makes life easier on the client side
        bundle.data['repeat'] = bundle.obj.rule is not None
        bundle.data['allDay'] = bundle.data.pop('all_day')
        return bundle


    def build_filters(self, filters=None): 
        '''
        Currently, some clients (like arshaw's FullCalendar) send time 
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
    calendar = fields.ForeignKey('tastycal.api.CalendarResource', 'calendar')
    events = fields.ToManyField(EventResource, 'events', null=True)

    #===========================================================================
    class Meta:
        queryset = RRule.objects.all()
        resource_name = 'rrule'
        collection_name = 'rrules'
        authorization = Authorization()
        authentication = Authentication()


    def alter_deserialized_detail_data(self, request, data):
        if getattr(self, 'parent_calendar', None):
            data['calendar'] = self.parent_calendar
        return data

    def obj_create(self, bundle, request=None, **kwargs):
        """
        Repeating events are persisted as soon as the rule is created
        so, in addition to creating the event, the resource must generate
        a list of events associated with the rule.
        """
        bundle = super(RRuleResource, self).obj_create(bundle, **kwargs)
        # bundle.obj.generate_events()
        return bundle


#===============================================================================
class CalendarResource(ModelResource):
    events = fields.ToManyField(EventResource, 'events', null=True)
    rules = fields.ToManyField(RRuleResource, 'rules', null=True)

    #===========================================================================
    class Meta:
        queryset = Calendar.objects.all()
        resource_name = 'calendar'
        collection_name = 'calendars'
        authorization = Authorization()
        authentication= Authentication()
        filtering = {
            'id': ALL,
        }

    def prepend_urls(self):
        return [
            url(r"(?P<resource_name>%s)/(?P<pk>\w+)/events%s$" % (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('dispatch_event_list'), 
                name="api_dispatch_event_list"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w+)/rules%s$" % (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('dispatch_rule_list'), 
                name="api_dispatch_rule_list"),
        ]

    # def alter_deserialized_detail_data(self, request, data):
    def dispatch_event_list(self, request, **kwargs):
        cal_pk = kwargs.pop('pk')
        event_resource = EventResource()
        event_resource.parent_calendar = {'pk': cal_pk, }

        kwargs['calendar__id'] = cal_pk
        return event_resource.dispatch('list', request, **kwargs)

    def dispatch_rule_list(self, request, **kwargs):
        cal_pk = kwargs.pop('pk')
        rule_resource = RRuleResource()
        rule_resource.parent_calendar = {'pk': cal_pk, }

        kwargs['calendar__id'] = cal_pk
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
