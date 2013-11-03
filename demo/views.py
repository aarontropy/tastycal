from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
import json

from tastycal.models import Calendar
from tastycal.api import CalendarResource


def jquery_view(request, calendar_id):
	calendar = get_object_or_404(Calendar, id=calendar_id)
	cr = CalendarResource()
	cal_bundle = cr.build_bundle(obj=calendar, request=request)
	cal_bundle = cr.full_dehydrate(cal_bundle)


	calendar_data = {
		'calendar_uri': cal_bundle.data.get('resource_uri',''),
		'events_uri': cal_bundle.data['events_uri'],
		'repeats_uri': cal_bundle.data['rules_uri'],
	}

	return render_to_response( 
		'jquery.html', 
		{'calendar_data': json.dumps(calendar_data)}, 
		context_instance=RequestContext(request)
	)

