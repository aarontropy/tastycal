# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Calendar'
        db.create_table(u'tastycal_calendar', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('parent_calendar', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='child_calendars', null=True, to=orm['tastycal.Calendar'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'tastycal', ['Calendar'])

        # Adding model 'RRule'
        db.create_table(u'tastycal_rrule', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('calendar', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rules', to=orm['tastycal.Calendar'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('duration', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('all_day', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('timezone', self.gf('tastycal.timezone_field.fields.TimeZoneField')(null=True)),
            ('dtstart', self.gf('django.db.models.fields.DateTimeField')()),
            ('freq', self.gf('django.db.models.fields.PositiveIntegerField')(default=2, blank=True)),
            ('interval', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('count', self.gf('django.db.models.fields.PositiveIntegerField')(blank=True)),
            ('until', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('wkst', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('byweekday', self.gf('tastycal.fields.IntegerListField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'tastycal', ['RRule'])

        # Adding model 'EventType'
        db.create_table(u'tastycal_eventtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('abbr', self.gf('django.db.models.fields.CharField')(unique=True, max_length=4)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'tastycal', ['EventType'])

        # Adding model 'Event'
        db.create_table(u'tastycal_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('calendar', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'events', to=orm['tastycal.Calendar'])),
            ('rule', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'events', null=True, to=orm['tastycal.RRule'])),
            ('event_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tastycal.EventType'], null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('all_day', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('timezone', self.gf('tastycal.timezone_field.fields.TimeZoneField')(null=True)),
        ))
        db.send_create_signal(u'tastycal', ['Event'])


    def backwards(self, orm):
        # Deleting model 'Calendar'
        db.delete_table(u'tastycal_calendar')

        # Deleting model 'RRule'
        db.delete_table(u'tastycal_rrule')

        # Deleting model 'EventType'
        db.delete_table(u'tastycal_eventtype')

        # Deleting model 'Event'
        db.delete_table(u'tastycal_event')


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
            'Meta': {'ordering': "('start', 'end', 'title')", 'object_name': 'Event'},
            'all_day': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'calendar': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'events'", 'to': u"orm['tastycal.Calendar']"}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'event_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tastycal.EventType']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rule': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'events'", 'null': 'True', 'to': u"orm['tastycal.RRule']"}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'timezone': ('tastycal.timezone_field.fields.TimeZoneField', [], {'null': 'True'}),
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
            'byweekday': ('tastycal.fields.IntegerListField', [], {'null': 'True', 'blank': 'True'}),
            'calendar': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rules'", 'to': u"orm['tastycal.Calendar']"}),
            'count': ('django.db.models.fields.PositiveIntegerField', [], {'blank': 'True'}),
            'dtstart': ('django.db.models.fields.DateTimeField', [], {}),
            'duration': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'freq': ('django.db.models.fields.PositiveIntegerField', [], {'default': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interval': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'timezone': ('tastycal.timezone_field.fields.TimeZoneField', [], {'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'until': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'wkst': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['tastycal']