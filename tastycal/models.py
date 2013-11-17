from datetime import datetime, date, timedelta

from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.forms.models import model_to_dict
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from dateutil import rrule

from fields import IntegerListField
from tastycal.timezone_field import TimeZoneField


#===============================================================================
class Calendar(models.Model):
    '''
    A container for events which can be attached to an arbitrary object

    '''
    title = models.CharField(_('title'), max_length=32)
    parent_calendar = models.ForeignKey('self', blank=True, null=True, related_name="child_calendars")

    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
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
        return self.events.filter(start__gte=datetime.now())


    def next_event(self):
        '''
        Return the single occurrence set to start on or after the current time
        if available, otherwise ``None``.
        '''
        upcoming = self.upcoming_events()
        return upcoming and upcoming[0] or None



#===============================================================================
class RRuleManager(models.Manager):
    def split_rule(split_rule, with_rule, on_date):
        '''
        '''
        pass


#===============================================================================
class RRule(models.Model):
    '''
    An object which stores the options for the python-dateutil module
    capable of generating a set of events

    '''
    (
    YEARLY,
    MONTHLY,
    WEEKLY,
    DAILY,
    HOURLY,
    MINUTELY,
    SECONDLY) = list(range(7))

    WEEKDAYS = (
        (0,'MO'),
        (1,'TU'),
        (2,'WE'),
        (3,'TH'),
        (4,'FR'),
        (5,'SA'),
        (6,'SU'),
    )
    calendar = models.ForeignKey(Calendar, related_name="rules")

    # Default Repeating Event Information
    title = models.CharField(_('title'), max_length=100)            
    duration = models.PositiveIntegerField(blank=True, null=True, default=0)   # Duration of event in minutes

    end = models.DateTimeField(_('end time'), null=True, blank=True)
    all_day = models.BooleanField(_('all day'), default=False)
    timezone = TimeZoneField(null=True)

    # RRule parameters
    dtstart = models.DateTimeField(_('dtstart'))
    freq = models.PositiveIntegerField(default=rrule.WEEKLY, blank=True)
    interval = models.PositiveIntegerField(default=1)
    count = models.PositiveIntegerField(blank=True)
    until = models.DateTimeField(blank=True, null=True)
    wkst = models.PositiveIntegerField(choices=WEEKDAYS, default=0)
    byweekday = IntegerListField(blank=True, null=True)


    #===========================================================================
    class Meta:
        verbose_name = _('recurrence rule')
        verbose_name_plural = _('recurrence rules')

    def __init__(self, *args, **kwargs):
        super(RRule, self).__init__(*args, **kwargs)
        self._rrule = None
        

    def __unicode__(self):
        return "Event rule for %s" % self.calendar.title


    def save(self, *args, **kwargs):
        super(RRule, self).save(*args, **kwargs)
        self.generate_events()


    def delete(self, *args, **kwargs):
        """
        deletes all events related to this rule
        deletes rule normally
        """
        for ev in self.events.all():
            ev.delete()
        super(RRule, self).delete(*args, **kwargs)

    def get_rrule(self):
        if self._rrule is None:
            # if it isn't cached, create it
            params = model_to_dict(self, fields=['dtstart', 'freq','until','count','interval','wkst','byweekday']) 
            params['wkst'] = rrule.weekday(params['wkst'])
            if len(self.byweekday) == 0:
                params.pop('byweekday')
            if not params['count'] and not params['until']:
                params['count'] = 1
            self._rrule = rrule.rrule(**params)
        return self._rrule

    def generate_events(self):
        '''
        Creates a set of events based on the model's rrule options

        '''
        events = self.get_rrule()

        for ev in self.events.all():
            ev.delete()

        for ev in events:
            Event.objects.create(
                start = ev,
                end = ev + timedelta(minutes=self.duration) if self.duration > 0 else None,
                all_day = self.all_day,
                title = self.title,
                calendar = self.calendar,
                rule = self,
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
    rule = models.ForeignKey(RRule, blank=True, null=True, related_name=_('events'))
    event_type = models.ForeignKey(EventType, verbose_name=_('event type'), null=True, blank=True)

    title = models.CharField(_('title'), max_length=100)
    start = models.DateTimeField(_('start time'))
    end = models.DateTimeField(_('end time'), blank=True, null=True)
    all_day = models.BooleanField(_('all day'), default=False)
    timezone = TimeZoneField(null=True)


    #===========================================================================
    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')
        ordering = ('start', 'end', 'title')


    def __unicode__(self):
        return u'%s: %s' % (self.title, self.start.isoformat())


    def save(self, *args, **kwargs):
        if not self.end:
            self.all_day = True

        # Strip any timezone information from 'start' and 'end'
        # Timezone must be passed separately.
        self.start = self.start.replace(tzinfo=None)
        if self.end:
            self.end = self.end.replace(tzinfo=None)

        super(Event, self).save(*args, **kwargs)




    def get_start(self):
        pass

    def get_date(self):
        pass

    def __cmp__(self, other):
        return cmp(self.start, other.start)

