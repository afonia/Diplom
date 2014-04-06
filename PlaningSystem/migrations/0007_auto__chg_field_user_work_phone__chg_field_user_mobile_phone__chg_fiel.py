# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'User.work_phone'
        db.alter_column('PlaningSystem_user', 'work_phone', self.gf('django.db.models.fields.CharField')(max_length=300, null=True))

        # Changing field 'User.mobile_phone'
        db.alter_column('PlaningSystem_user', 'mobile_phone', self.gf('django.db.models.fields.CharField')(max_length=300, null=True))

        # Changing field 'User.third_name'
        db.alter_column('PlaningSystem_user', 'third_name', self.gf('django.db.models.fields.CharField')(max_length=300, null=True))

    def backwards(self, orm):

        # Changing field 'User.work_phone'
        db.alter_column('PlaningSystem_user', 'work_phone', self.gf('django.db.models.fields.CharField')(max_length=300, default=''))

        # Changing field 'User.mobile_phone'
        db.alter_column('PlaningSystem_user', 'mobile_phone', self.gf('django.db.models.fields.CharField')(max_length=300, default=''))

        # Changing field 'User.third_name'
        db.alter_column('PlaningSystem_user', 'third_name', self.gf('django.db.models.fields.CharField')(max_length=300, default=''))

    models = {
        'PlaningSystem.rate': {
            'Meta': {'object_name': 'Rate'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'PlaningSystem.schedule': {
            'Meta': {'object_name': 'Schedule'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'workplace': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['PlaningSystem.Workplace']"})
        },
        'PlaningSystem.timecost': {
            'Meta': {'object_name': 'TimeCost'},
            'cost': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PlaningSystem.Rate']"}),
            'since': ('django.db.models.fields.DateTimeField', [], {}),
            'to': ('django.db.models.fields.DateTimeField', [], {})
        },
        'PlaningSystem.user': {
            'Meta': {'object_name': 'User'},
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '1000', 'default': "''", 'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'user_set'", 'blank': 'True', 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'mobile_phone': ('django.db.models.fields.CharField', [], {'max_length': '300', 'default': "''", 'null': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'third_name': ('django.db.models.fields.CharField', [], {'max_length': '300', 'default': "''", 'null': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'user_set'", 'blank': 'True', 'to': "orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'}),
            'work_phone': ('django.db.models.fields.CharField', [], {'max_length': '300', 'default': "''", 'null': 'True'}),
            'workplaces': ('django.db.models.fields.related.ManyToManyField', [], {'default': "''", 'symmetrical': 'False', 'null': 'True', 'to': "orm['PlaningSystem.Workplace']"})
        },
        'PlaningSystem.userwish': {
            'Meta': {'object_name': 'UserWish'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isApproved': ('django.db.models.fields.BooleanField', [], {}),
            'since': ('django.db.models.fields.DateTimeField', [], {}),
            'to': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PlaningSystem.User']"}),
            'wish': ('django.db.models.fields.related.ForeignKey', [], {'default': "''", 'null': 'True', 'to': "orm['PlaningSystem.WishEnum']"}),
            'workingShift': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PlaningSystem.WorkingShift']"})
        },
        'PlaningSystem.wishenum': {
            'Meta': {'object_name': 'WishEnum'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '1000', 'default': "''", 'null': 'True', 'blank': 'True'}),
            'wish': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'PlaningSystem.workingshift': {
            'Meta': {'object_name': 'WorkingShift'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '1000', 'default': "''", 'null': 'True', 'blank': 'True'}),
            'scheldue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PlaningSystem.Schedule']"}),
            'since': ('django.db.models.fields.DateTimeField', [], {}),
            'to': ('django.db.models.fields.DateTimeField', [], {})
        },
        'PlaningSystem.workplace': {
            'Meta': {'object_name': 'Workplace'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'rates': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'null': 'True', 'to': "orm['PlaningSystem.Rate']"})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'blank': 'True', 'to': "orm['auth.Permission']"})
        },
        'auth.permission': {
            'Meta': {'object_name': 'Permission', 'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'object_name': 'ContentType', 'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['PlaningSystem']