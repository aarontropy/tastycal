# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Event.end_time'
        db.alter_column(u'tastycal_event', 'end_time', self.gf('django.db.models.fields.DateTimeField')(null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Event.end_time'
        raise RuntimeError("Cannot reverse this migration. 'Event.end_time' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Event.end_time'
        db.alter_column(u'tastycal_event', 'end_time', self.gf('django.db.models.fields.DateTimeField')())

    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'tastycal.calendar': {
            'Meta': {'object_name': 'Calendar'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent_calendar': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'child_calendars'", 'null': 'True', 'to': u"orm['tastycal.Calendar']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'tastycal.event': {
            'Meta': {'ordering': "('start_time', 'end_time', 'title')", 'object_name': 'Event'},
            'all_day': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'calendar': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'events'", 'to': u"orm['tastycal.Calendar']"}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'event_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tastycal.EventType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rule': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'events'", 'null': 'True', 'to': u"orm['tastycal.RRule']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'tastycal.eventtype': {
            'Meta': {'object_name': 'EventType'},
            'abbr': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '4'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'tastycal.rrule': {
            'Meta': {'object_name': 'RRule'},
            'all_day': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'byweekday': ('tastycal.fields.RRuleWeekdayListField', [], {'max_length': '50'}),
            'calendar': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rules'", 'to': u"orm['tastycal.Calendar']"}),
            'count': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'freq': ('django.db.models.fields.PositiveIntegerField', [], {'default': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interval': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'until': ('django.db.models.fields.DateTimeField', [], {}),
            'wkst': ('tastycal.fields.RRuleWeekdayField', [], {})
        }
    }

    complete_apps = ['tastycal']