from django.test import TestCase
from tastypie.test import ResourceTestCase
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import pytz
import json

from tastycal.models import Event, Calendar, RRule

EST = 'America/Kentucky/Louisville'
PST = 'America/Los_Angeles'  # pytz.tzinfo.DstTzInfo
GMT = 'Etc/GMT'              # pytz.tzinfo.StaticTzInfo
UTC = 'UTC'                  # pytz.UTC singleton

EST_tz = pytz.timezone(EST)
PST_tz = pytz.timezone(PST)
GMT_tz = pytz.timezone(GMT)
UTC_tz = pytz.timezone(UTC)

class EventTestCase(TestCase):
    def setUp(self):
        self.d = datetime(1976, 12, 14, 6,30, tzinfo=EST_tz)
        self.calendar = Calendar.objects.create(title='Test Calendar')
        e = Event.objects.create(title='Test Event', start=self.d, calendar=self.calendar)


    def test_start_date_stored_as_UTC(self):
        self.assertEqual(self.calendar.events.all()[0].start.tzinfo, UTC_tz)

    def test_date_integrity(self):
        self.assertEqual(self.calendar.events.all()[0].start, self.d)

    def test_recurrence_create_and_delete(self):
        number_of_events = len(self.calendar.events.all())

        r = RRule.objects.create(
            calendar=self.calendar,
            title='Test Rule',
            dtstart=self.d,
            freq=RRule.WEEKLY,
            duration=60,
            interval=1,
            count=2
            )
        # Number of events created
        self.assertEqual(len(r.events.all()), 2)
        # duration of event is 60 minutes
        e = r.events.all()[0]
        td = e.end - e.start
        self.assertEqual(td.seconds/60, r.duration)
        # events are spaced 1 week apart
        e1 = r.events.all()[0]
        e2 = r.events.all()[1]
        self.assertEqual(e1.start + timedelta(days=7), e2.start)
        # Deleting rule deletes events
        r.delete()
        self.assertEqual(len(self.calendar.events.all()), number_of_events)


class APITestCase(ResourceTestCase):
    def setUp(self):
        super(APITestCase, self).setUp()

        # Create a user.
        self.username = 'aaron'
        self.password = 'pass'
        self.user = User.objects.create_superuser(self.username, 'aaron@example.com', self.password)

        # Create a calendar for test use
        self.calendar_1 = Calendar.objects.create(title='Test Calendar 1')
        self.calendar_2 = Calendar.objects.create(title='Test Calendar 2')
        self.calendar_detail_url_1 = '/api/v1/calendar/%d/' % self.calendar_1.id
        self.calendar_detail_url_2 = '/api/v1/calendar/%d/' % self.calendar_2.id

        self.d = datetime(1976, 12, 14, 6,30, tzinfo=EST_tz)

        # Various uris
        self.calendar_list = '/api/v1/calendar/'
        self.event_list = '/api/v1/event/'

        # POST Data
        # We'll send this data to post urls
        self.post_event_data = {
            'title': 'Test Event',
            'calendar': self.calendar_detail_url_1,
            'start': self.d,
            'end': self.d + timedelta(minutes=60)
        }


    def get_credentials(self):
        return self.create_basic(username=self.username, password=self.password)

    # def test_get_list_unauthorized(self):
    #     self.assertHttpUnauthorized(self.api_client.get('/api/v1/calendar/'))

    def test_get_calendar_list_json(self):
        resp = self.api_client.get('/api/v1/calendar/', format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)

        # Scope out the data for correctness.
        self.assertEqual(len(self.deserialize(resp)['calendars']), 2)
        # Here, we're checking an entire structure for the expected data.
        cal = self.deserialize(resp)['calendars'][0]
        self.assertEqual(cal['id'], self.calendar_1.pk)
        self.assertEqual(cal['title'], 'Test Calendar 1')

    def test_post_event(self):
        self.api_client.client.login(username=self.username, password=self.password)

        self.assertEqual(self.calendar_1.events.count(), 0)
        resp = self.api_client.post(self.event_list, format='json', data=self.post_event_data, authentication=self.get_credentials) 

        self.assertHttpCreated(resp)
        self.assertEqual(self.calendar_1.events.count(), 1)

        self.api_client.client.logout()
        
    def test_post_event_to_calendar(self):
        self.api_client.client.login(username=self.username, password=self.password)

        # grab the first calendar
        resp = self.api_client.get('/api/v1/calendar/', format='json', authentication=self.get_credentials())
        cal = self.deserialize(resp)['calendars'][0]

        # Check the current number of events
        print "URL"
        print cal['events_uri']
        self.assertEqual(len(cal['events']), 0)
        resp =self.api_client.post(cal['events_uri'], format='json', data=self.post_event_data, authentication=self.get_credentials)
        self.assertHttpCreated(resp)
        self.assertEqual(self.calendar_1.events.count(), 1)

        self.api_client.client.logout()


    def test_retrieve_timezone_correct_datetime(self):
        self.api_client.client.login(username=self.username, password=self.password)

        event_data = {
            'title': 'Test Event',
            'start': self.d.strftime("%m/%d/%y %H:%M"),
            'end': (self.d + timedelta(minutes=60)).strftime("%m/%d/%y %H:%M"),
            'calendar': self.calendar_detail_url_1
        }
        json_event = json.dumps(event_data)

        events_uri = '%s%s' % (self.calendar_detail_url_1, 'events/')

        resp = self.api_client.post(self.event_list, format='json', data=event_data, authentication=self.get_credentials)
        self.assertHttpCreated(resp)

        get_resp = self.api_client.get(events_uri, format='json', authentication=self.get_credentials)
        e = self.deserialize(get_resp)['events'][0]
        print self.d
        print e['start']
        self.assertEqual(e.start, self.d)

        self.api_client.client.logout()



