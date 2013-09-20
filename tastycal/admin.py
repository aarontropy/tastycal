from django.contrib.contenttypes import generic
from django.contrib import admin
from tastycal.models import Calendar, Event, RRule, EventType



#===============================================================================
class CalendarAdmin(admin.ModelAdmin):
    pass

#===============================================================================
class RRuleAdmin(admin.ModelAdmin):
    pass

#===============================================================================
class EventAdmin(admin.ModelAdmin):
    list_display = ('calendar', 'title')
    search_fields = ('title', 'description')

class EventTypeAdmin(admin.ModelAdmin):
    pass


admin.site.register(Calendar, CalendarAdmin)
admin.site.register(RRule, RRuleAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(EventType, EventTypeAdmin)
