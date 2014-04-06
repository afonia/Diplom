# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'WishEnum.image'
        db.add_column('PlaningSystem_wishenum', 'image',
                      self.gf('django.db.models.fields.files.ImageField')(blank=True, default='', null=True, max_length=1000),
                      keep_default=False)

        # Adding field 'WorkingShift.image'
        db.add_column('PlaningSystem_workingshift', 'image',
                      self.gf('django.db.models.fields.files.ImageField')(blank=True, default='', null=True, max_length=1000),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'WishEnum.image'
        db.delete_column('PlaningSystem_wishenum', 'image')

        # Deleting field 'WorkingShift.image'
        db.delete_column('PlaningSystem_workingshift', 'image')


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
            'workplace': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['PlaningSystem.Workplace']", 'unique': 'True'})
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
            'avatar': ('django.db.models.fields.files.ImageField', [], {'blank': 'True', 'default': "''", 'null': 'True', 'max_length': '1000'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True', 'related_name': "'user_set'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True', 'related_name': "'user_set'"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'workplaces': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['PlaningSystem.Workplace']", 'default': "''", 'symmetrical': 'False', 'null': 'True'})
        },
        'PlaningSystem.userwish': {
            'Meta': {'object_name': 'UserWish'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isApproved': ('django.db.models.fields.BooleanField', [], {}),
            'since': ('django.db.models.fields.DateTimeField', [], {}),
            'to': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PlaningSystem.User']"}),
            'wish': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PlaningSystem.WishEnum']", 'default': "''", 'null': 'True'}),
            'workingShift': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PlaningSystem.WorkingShift']"})
        },
        'PlaningSystem.wishenum': {
            'Meta': {'object_name': 'WishEnum'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'blank': 'True', 'default': "''", 'null': 'True', 'max_length': '1000'}),
            'wish': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'PlaningSystem.workingshift': {
            'Meta': {'object_name': 'WorkingShift'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'blank': 'True', 'default': "''", 'null': 'True', 'max_length': '1000'}),
            'scheldue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PlaningSystem.Schedule']"}),
            'since': ('django.db.models.fields.DateTimeField', [], {}),
            'to': ('django.db.models.fields.DateTimeField', [], {})
        },
        'PlaningSystem.workplace': {
            'Meta': {'object_name': 'Workplace'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'rates': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['PlaningSystem.Rate']", 'symmetrical': 'False', 'null': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'object_name': 'Permission', 'unique_together': "(('content_type', 'codename'),)", 'ordering': "('content_type__app_label', 'content_type__model', 'codename')"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'object_name': 'ContentType', 'unique_together': "(('app_label', 'model'),)", 'ordering': "('name',)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['PlaningSystem']