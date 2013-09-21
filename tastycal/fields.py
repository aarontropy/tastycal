from django.db import models
from dateutil import rrule

# rrule.MO = 0, etc.
weekdays = [rrule.MO, rrule.TU, rrule.WE, rrule.TH, rrule.FR, rrule.SA, rrule.SU]
MO, TU, WE, TH, FR, SA, SU = list(range(7))

class RRuleWeekdayField(models.IntegerField):
    """
    rrule.weekday is a callable object that takes 2 arguments, neither of which
    have defaults.  This causes problems when djange has logic like:
    if callable(thing):
        thing()  # <- only one argument (self)
    This stores an in
    """
    description = "Model field to contain dateutil.rrule.weekday object"

    def to_python(self, value):
        def new_call(self, n=None):
            if n == self.n:
                return self
            else:
                return self.__class__(self.weekday, n)

        if isinstance(value, rrule.weekday):
            value.__call__ = new_call
            return value

        ret = weekdays[value]
        ret.__call__ = new_call
        return ret


    def get_prep_value(self, value):
        return value.weekday if value is not None else None

    def get_default(self):
        """
        Returns the default value for this field.
        Overriding this method because rrule.weekday is callable AND it takes
        2 arguments.  So when the regular version of this method calls it with
        one argument (self), it throws an error.
        """
        if self.has_default():
            if callable(self.default):
                return self.default(n=None)
            return force_text(self.default, strings_only=True)
        if (not self.empty_strings_allowed or (self.null and
                   not connection.features.interprets_empty_strings_as_nulls)):
            return None
        return ""


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
