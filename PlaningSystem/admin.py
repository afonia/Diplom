#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .forms import AdminUserChangeForm, AdminUserAddForm
from .models import User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _
# Register your models here.
from PlaningSystem.models import *

class UserSettingsInline(admin.StackedInline):
    model = UserSettings
class UserAdmin(BaseUserAdmin):
    form = AdminUserChangeForm
    add_form = AdminUserAddForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (
            'first_name',
            'last_name',
            'third_name',
            'email',
            'work_phone',
            'mobile_phone',
            'avatar',
            # 'settings',
            'workplaces'
        )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')}
        ),
    )
    inlines = (UserSettingsInline,)

admin.site.register(User, UserAdmin)

class RateAdmin(admin.ModelAdmin):
    list_display = ('name',)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('pub_date', 'text',)

class TimeCostAdmin(admin.ModelAdmin):
    list_display = ('rate',)

class WishEnumAdmin(admin.ModelAdmin):
    list_display = ('wish',)

class WorkplaceAdmin(admin.ModelAdmin):
    list_display = ('name',)

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('name',)

class WorkingShiftAdmin(admin.ModelAdmin):
    list_display = ('since', 'to', 'scheldue')

# class UserAdmin(admin.ModelAdmin):
#     list_display = ('name',)

class UserWishAdmin(admin.ModelAdmin):
    list_display = ('user',)

class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user',)



admin.site.register(Rate, RateAdmin)
admin.site.register(UserSettings, UserSettingsAdmin)
admin.site.register(TimeCost, TimeCostAdmin)
admin.site.register(WishEnum, WishEnumAdmin)
admin.site.register(Workplace, WorkplaceAdmin)
admin.site.register(WorkingShift, WorkingShiftAdmin)
# admin.site.register(User, UserAdmin)
admin.site.register(UserWish, UserWishAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Notification, NotificationAdmin)


