from django.db import models
from dateutil import rrule

# rrule.MO = 0, etc.
weekdays = [rrule.MO, rrule.TU, rrule.WE, rrule.TH, rrule.FR, rrule.SA, rrule.SU]

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun','Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

class RRuleWeekdayField(models.IntegerField):

	description = "Model field to contain dateutil.rrule.weekday object"

	def to_python(self, value):
		if isinstance(value, rrule.weekday):
			return value

		return weekdays[value]

	def get_prep_value(self, value):
		return value.weekday


class RRuleWeekdayListField(models.CharField):
	'''
	Weekdays will be stored in a charfield as a comma-separated list of integers

	'''

	description = "A list of dateutil.rrule.weekday objects"

	def __init__(self, *args, **kwargs):
		kwargs['max_length'] = 50
		super(RRuleWeekdayListField, self).__init__(*args, **kwargs)

	def to_python(self,value):
		if isinstance(value, list):
			return value

		return [int(s) for s in value.split(',')]

	def get_prep_value(self, value):
		return ','.join([str(d) for d in value])


class RRuleMonthListField(models.CharField):
	'''
	Months are represented by integers (Jan=1, Dec=12)
	Months will be stored in a charfield as a comma-separated list of integers

	'''

	description = "A list of integers representing months"
	
	def __init__(self, *args, **kwargs):
		kwargs['max_length'] = 50
		super(RRuleMonthListField, self).__init__(*args, **kwargs)

	def to_python(self,value):
		if isinstance(value, list):
			return value

		return [int(s) for s in value.split(',')]

	def get_prep_value(self, value):
		return ','.join([str(d) for d in value])

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^tastycal\.fields\.RRuleWeekdayField"])
add_introspection_rules([], ["^tastycal\.fields\.RRuleWeekdayListField"])
add_introspection_rules([], ["^tastycal\.fields\.RRuleMonthListField"])
