# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Rate'
        db.create_table('PlaningSystem_rate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal('PlaningSystem', ['Rate'])

        # Adding model 'TimeCost'
        db.create_table('PlaningSystem_timecost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('since', self.gf('django.db.models.fields.DateTimeField')()),
            ('to', self.gf('django.db.models.fields.DateTimeField')()),
            ('cost', self.gf('django.db.models.fields.FloatField')()),
            ('rate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PlaningSystem.Rate'])),
        ))
        db.send_create_signal('PlaningSystem', ['TimeCost'])

        # Adding model 'WishEnum'
        db.create_table('PlaningSystem_wishenum', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('wish', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(null=True, blank=True, max_length=1000, default='')),
            ('weight', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('PlaningSystem', ['WishEnum'])

        # Adding model 'Workplace'
        db.create_table('PlaningSystem_workplace', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal('PlaningSystem', ['Workplace'])

        # Adding M2M table for field rates on 'Workplace'
        m2m_table_name = db.shorten_name('PlaningSystem_workplace_rates')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('workplace', models.ForeignKey(orm['PlaningSystem.workplace'], null=False)),
            ('rate', models.ForeignKey(orm['PlaningSystem.rate'], null=False))
        ))
        db.create_unique(m2m_table_name, ['workplace_id', 'rate_id'])

        # Adding model 'Schedule'
        db.create_table('PlaningSystem_schedule', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('workplace', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, null=True, to=orm['PlaningSystem.Workplace'], unique=True)),
        ))
        db.send_create_signal('PlaningSystem', ['Schedule'])

        # Adding model 'WorkingShift'
        db.create_table('PlaningSystem_workingshift', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('since', self.gf('django.db.models.fields.DateTimeField')()),
            ('to', self.gf('django.db.models.fields.DateTimeField')()),
            ('image', self.gf('django.db.models.fields.files.ImageField')(null=True, blank=True, max_length=1000, default='')),
            ('scheldue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PlaningSystem.Schedule'])),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 5, 23, 0, 0))),
        ))
        db.send_create_signal('PlaningSystem', ['WorkingShift'])

        # Adding model 'User'
        db.create_table('PlaningSystem_user', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(blank=True, max_length=30)),
            ('last_name', self.gf('django.db.models.fields.CharField')(blank=True, max_length=30)),
            ('email', self.gf('django.db.models.fields.EmailField')(blank=True, max_length=75)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('avatar', self.gf('django.db.models.fields.files.ImageField')(null=True, blank=True, max_length=1000, default='')),
            ('third_name', self.gf('django.db.models.fields.CharField')(null=True, blank=True, max_length=300, default='')),
            ('work_phone', self.gf('django.db.models.fields.CharField')(null=True, blank=True, max_length=300, default='')),
            ('mobile_phone', self.gf('django.db.models.fields.CharField')(null=True, blank=True, max_length=300, default='')),
        ))
        db.send_create_signal('PlaningSystem', ['User'])

        # Adding M2M table for field groups on 'User'
        m2m_table_name = db.shorten_name('PlaningSystem_user_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm['PlaningSystem.user'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'User'
        m2m_table_name = db.shorten_name('PlaningSystem_user_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm['PlaningSystem.user'], null=False)),
            ('permission', models.ForeignKey(orm['auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'permission_id'])

        # Adding M2M table for field workplaces on 'User'
        m2m_table_name = db.shorten_name('PlaningSystem_user_workplaces')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm['PlaningSystem.user'], null=False)),
            ('workplace', models.ForeignKey(orm['PlaningSystem.workplace'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'workplace_id'])

        # Adding model 'UserSettings'
        db.create_table('PlaningSystem_usersettings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shiftDenied', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('shiftActived', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('shiftsInMonth', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True, default=5)),
            ('nightShift', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(null=True, to=orm['PlaningSystem.User'], unique=True)),
        ))
        db.send_create_signal('PlaningSystem', ['UserSettings'])

        # Adding model 'Notification'
        db.create_table('PlaningSystem_notification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=5000)),
            ('page', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('mail', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PlaningSystem.User'])),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 5, 23, 0, 0))),
        ))
        db.send_create_signal('PlaningSystem', ['Notification'])

        # Adding model 'UserWish'
        db.create_table('PlaningSystem_userwish', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('since', self.gf('django.db.models.fields.DateTimeField')()),
            ('to', self.gf('django.db.models.fields.DateTimeField')()),
            ('wish', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, null=True, to=orm['PlaningSystem.WishEnum'], default='')),
            ('isApproved', self.gf('django.db.models.fields.BooleanField')()),
            ('workingShift', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PlaningSystem.WorkingShift'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PlaningSystem.User'])),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 5, 23, 0, 0))),
        ))
        db.send_create_signal('PlaningSystem', ['UserWish'])


    def backwards(self, orm):
        # Deleting model 'Rate'
        db.delete_table('PlaningSystem_rate')

        # Deleting model 'TimeCost'
        db.delete_table('PlaningSystem_timecost')

        # Deleting model 'WishEnum'
        db.delete_table('PlaningSystem_wishenum')

        # Deleting model 'Workplace'
        db.delete_table('PlaningSystem_workplace')

        # Removing M2M table for field rates on 'Workplace'
        db.delete_table(db.shorten_name('PlaningSystem_workplace_rates'))

        # Deleting model 'Schedule'
        db.delete_table('PlaningSystem_schedule')

        # Deleting model 'WorkingShift'
        db.delete_table('PlaningSystem_workingshift')

        # Deleting model 'User'
        db.delete_table('PlaningSystem_user')

        # Removing M2M table for field groups on 'User'
        db.delete_table(db.shorten_name('PlaningSystem_user_groups'))

        # Removing M2M table for field user_permissions on 'User'
        db.delete_table(db.shorten_name('PlaningSystem_user_user_permissions'))

        # Removing M2M table for field workplaces on 'User'
        db.delete_table(db.shorten_name('PlaningSystem_user_workplaces'))

        # Deleting model 'UserSettings'
        db.delete_table('PlaningSystem_usersettings')

        # Deleting model 'Notification'
        db.delete_table('PlaningSystem_notification')

        # Deleting model 'UserWish'
        db.delete_table('PlaningSystem_userwish')


    models = {
        'PlaningSystem.notification': {
            'Meta': {'object_name': 'Notification'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mail': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'page': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 5, 23, 0, 0)'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '5000'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PlaningSystem.User']"})
        },
        'PlaningSystem.rate': {
            'Meta': {'object_name': 'Rate'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'PlaningSystem.schedule': {
            'Meta': {'object_name': 'Schedule'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'workplace': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'null': 'True', 'to': "orm['PlaningSystem.Workplace']", 'unique': 'True'})
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
            'avatar': ('django.db.models.fields.files.ImageField', [], {'null': 'True', 'blank': 'True', 'max_length': '1000', 'default': "''"}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'user_set'", 'blank': 'True', 'to': "orm['auth.Group']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'mobile_phone': ('django.db.models.fields.CharField', [], {'null': 'True', 'blank': 'True', 'max_length': '300', 'default': "''"}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'third_name': ('django.db.models.fields.CharField', [], {'null': 'True', 'blank': 'True', 'max_length': '300', 'default': "''"}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'user_set'", 'blank': 'True', 'to': "orm['auth.Permission']", 'symmetrical': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'work_phone': ('django.db.models.fields.CharField', [], {'null': 'True', 'blank': 'True', 'max_length': '300', 'default': "''"}),
            'workplaces': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'null': 'True', 'to': "orm['PlaningSystem.Workplace']", 'symmetrical': 'False', 'default': "''"})
        },
        'PlaningSystem.usersettings': {
            'Meta': {'object_name': 'UserSettings'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nightShift': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'shiftActived': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'shiftDenied': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'shiftsInMonth': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True', 'default': '5'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'null': 'True', 'to': "orm['PlaningSystem.User']", 'unique': 'True'})
        },
        'PlaningSystem.userwish': {
            'Meta': {'object_name': 'UserWish'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isApproved': ('django.db.models.fields.BooleanField', [], {}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 5, 23, 0, 0)'}),
            'since': ('django.db.models.fields.DateTimeField', [], {}),
            'to': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PlaningSystem.User']"}),
            'wish': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'null': 'True', 'to': "orm['PlaningSystem.WishEnum']", 'default': "''"}),
            'workingShift': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PlaningSystem.WorkingShift']"})
        },
        'PlaningSystem.wishenum': {
            'Meta': {'object_name': 'WishEnum'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'null': 'True', 'blank': 'True', 'max_length': '1000', 'default': "''"}),
            'weight': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'wish': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'PlaningSystem.workingshift': {
            'Meta': {'object_name': 'WorkingShift'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'null': 'True', 'blank': 'True', 'max_length': '1000', 'default': "''"}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 5, 23, 0, 0)'}),
            'scheldue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PlaningSystem.Schedule']"}),
            'since': ('django.db.models.fields.DateTimeField', [], {}),
            'to': ('django.db.models.fields.DateTimeField', [], {})
        },
        'PlaningSystem.workplace': {
            'Meta': {'object_name': 'Workplace'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'rates': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'null': 'True', 'to': "orm['PlaningSystem.Rate']", 'symmetrical': 'False'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['auth.Permission']", 'symmetrical': 'False'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'db_table': "'django_content_type'", 'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType'},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['PlaningSystem']