from datetime import datetime, date, timedelta

from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.forms.models import model_to_dict
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from dateutil import rrule

from fields import RRuleWeekdayField, RRuleWeekdayListField


#===============================================================================
class Calendar(models.Model):
    '''
    A container for events which can be attached to an arbitrary object

    '''
    title = models.CharField(_('title'), max_length=32)
    parent_calendar = models.ForeignKey(Calendar, related_name="child_calendars")

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    #===========================================================================
    class Meta:
        verbose_name = _('calendar')
        verbose_name_plural = _('calendars')
        

    def __unicode__(self):
        return self.title


    def upcoming_events(self):
        '''
        Return all occurrences that are set to start on or after the current
        time.
        '''
        return self.events.filter(start_time__gte=datetime.now())


    def next_event(self):
        '''
        Return the single occurrence set to start on or after the current time
        if available, otherwise ``None``.
        '''
        upcoming = self.upcoming_events()
        return upcoming and upcoming[0] or None




#===============================================================================
class RRule(models.Model):
    '''
    An object which stores the options for the python-dateutil module
    capable of generating a set of events

    '''
    calendar = models.ForeignKey(Calendar, related_name="rules")

    title = models.CharField(_('title'), max_length=100)
    start_time = models.DateTimeField(_('start time'))
    end_time = models.DateTimeField(_('end time'), null=True)
    all_day = models.BooleanField(_('all day'), default=False)

    freq = models.PositiveIntegerField(default=rrule.WEEKLY)
    until = models.DateTimeField()
    count = models.PositiveIntegerField()
    interval = models.PositiveIntegerField()
    wkst = RRuleWeekdayField()
    byweekday = RRuleWeekdayListField()


    #===========================================================================
    class Meta:
        verbose_name = _('recurrence rule')
        verbose_name_plural = _('recurrence rules')
        

    def __unicode__(self):
        return "Event rule for %s" % self.calendar.title


    def generate_events(self):
        '''
        Creates a set of events based on the options stored
        Deletes previously-created child events and replaces with newly-created 
        ones, event if the old events have been edited.

        '''
        rrule_params = model_to_dict(self, fields=['freq','until','count','interval','wkst','byweekday']) 

        if not rrule_params['count'] and not rrule_params['until']:
            rrule_params['count'] = 1
        else:
            if not self.all_day and self.end_time is not None:
                delta = self.end_time - self.start_time
            else:
                delta = 0

            evs = rrule.rrule(dtstart=self.start_time, **rrule_params)
            if len(evs) > 0:
                # Since we've successfully created a list of events from our
                # rrule params, delete existing events linked to this rule.
                # This removes all edits a user has made, so this is not
                # ideal.
                for evo in self.events:
                    evo.delete()

            for ev in evs:
                self.events.create(
                    start_time=ev, 
                    end_time=ev + delta if self.end_time is not None else None,
                    all_day=self.all_day,
                    title=self.title,
                    calendar=self.calendar,
                )



#===============================================================================
class EventType(models.Model):
    '''
    Simple ``Event`` classifcation.
    
    '''
    abbr = models.CharField(_(u'abbreviation'), max_length=4, unique=True)
    label = models.CharField(_('label'), max_length=50)

    #===========================================================================
    class Meta:
        verbose_name = _('event type')
        verbose_name_plural = _('event types')
        

    def __unicode__(self):
        return self.label



#===============================================================================
class Event(models.Model):
    calendar = models.ForeignKey(Calendar, related_name=_('events'))
    rule = models.ForeignKey(EventRule, related_name=_('events'))
    event_type = models.ForeignKey(EventType, verbose_name=_('event type'))

    title = models.CharField(_('title'), max_length=100)
    notes = generic.GenericRelation(Note, verbose_name=_('notes'))
    start_time = models.DateTimeField(_('start time'))
    end_time = models.DateTimeField(_('end time'))
    all_day = models.BooleanField(_('all day'))


    #===========================================================================
    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')
        ordering = ('start_time', 'end_time', 'title')


    def __unicode__(self):
        return u'%s: %s' % (self.title, self.start_time.isoformat())


    @models.permalink
    def get_absolute_url(self):
        return ('swingtime-event', [str(self.id)])


    def __cmp__(self, other):
        return cmp(self.start_time, other.start_time)

