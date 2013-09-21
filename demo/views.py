from django.shortcuts import render_to_response
from django.template import RequestContext

from tastycal.models import Calendar


def jquery_view(request):
	calendars = Calendar.objects.all()

	return render_to_response('jquery.html', {'calendars': calendars}, context_instance=RequestContext(request))

