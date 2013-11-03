from datetime import datetime, date, timedelta

from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.forms.models import model_to_dict
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from dateutil import rrule

from fields import RRuleWeekdayListField


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

    title = models.CharField(_('title'), max_length=100)
    start = models.DateTimeField(_('start time'))
    end = models.DateTimeField(_('end time'), null=True, blank=True)
    all_day = models.BooleanField(_('all day'), default=False)

    freq = models.PositiveIntegerField(default=rrule.WEEKLY, blank=True)
    until = models.DateTimeField(blank=True, null=True)
    count = models.PositiveIntegerField(blank=True)
    interval = models.PositiveIntegerField(default=1)
    wkst = models.PositiveIntegerField(choices=WEEKDAYS, default=0)
    byweekday = RRuleWeekdayListField(blank=True)


    #===========================================================================
    class Meta:
        verbose_name = _('recurrence rule')
        verbose_name_plural = _('recurrence rules')
        

    def __unicode__(self):
        return "Event rule for %s" % self.calendar.title



    def delete(self, *args, **kwargs):
        """
        deletes all events related to this rule
        deletes rule normally
        """
        for ev in self.events.all():
            ev.delete()
        super(RRule, self).delete(*args, **kwargs)

    def generate_events(self):
        '''
        Creates a set of events based on the model's rrule options

        '''
        for ev in self.events.all():
            ev.delete()

        rrule_params = model_to_dict(self, fields=['freq','until','count','interval','wkst','byweekday']) 
        rrule_params['wkst'] = rrule.weekday(rrule_params['wkst'])
        if len(self.byweekday) == 0:
            rrule_params.pop('byweekday')

        if not rrule_params['count'] and not rrule_params['until']:
            rrule_params['count'] = 1
        else:
            if not self.all_day and self.end is not None:
                delta = self.end - self.start
            else:
                delta = timedelta(0)

            print rrule_params
            evs = rrule.rrule(dtstart=self.start, **rrule_params)
            for ev in evs:
                e = Event()
                e.start = ev
                e.end = ev + delta if self.end is not None else None
                e.all_day = self.all_day
                e.title = self.title
                e.calendar = self.calendar
                e.rule = self
                e.save()



                


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

        super(Event, self).save(*args, **kwargs)
        print self.start
        print self.end

    def delete(self, *args, **kwargs):
        super(Event, self).delete(*args, **kwargs)


    @models.permalink
    def get_absolute_url(self):
        return ('swingtime-event', [str(self.id)])


    def __cmp__(self, other):
        return cmp(self.start, other.start)

