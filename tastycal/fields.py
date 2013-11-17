from django.db import models
from dateutil import rrule
import pickle

# rrule.MO = 0, etc.
weekdays = [rrule.MO, rrule.TU, rrule.WE, rrule.TH, rrule.FR, rrule.SA, rrule.SU]
MO, TU, WE, TH, FR, SA, SU = list(range(7))


class IntegerListField(models.TextField):
    __metaclass__ = models.SubfieldBase
    description = "Stores a python list of integers"

    def __init__(self, *args, **kwargs):
        super(IntegerListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """ converts string of comma-separated integers to python list """
        if not value:
            value = []
        if isinstance(value, list):
            return value
        return [int(n) for n in value.split(',') if n.isdigit()]

    def get_prep_value(self, value):
        if value is None:
            return ''
        return ','.join([str(n) for n in value if isinstance(n,int)])

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)



class RRuleField(models.CharField):
    """
    Provides database store for dateutil.rrule objects.
    """
    description = "A dateutil rrule object"

    MAX_LENGTH = 800

    def __init__(self, *args, **kwargs):
        defaults = {
            'max_length': self.MAX_LENGTH,
        }
        defaults.update(kwargs)
        super(RRuleField, self).__init__(**defaults)


    def to_python(self, value):
        """ Convert to a rrule object """
        return pickle.loads(value)

    def get_prep_value(self, value):
        """ Convert to string representation of rrule """
        return pickle.dumps(value)


    def rrule_params(self):
        pass

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



# South support
try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules(patterns=['tastycal\.fields\.']
    )
