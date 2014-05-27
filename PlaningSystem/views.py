#!/usr/bin/env python
# -*- coding: utf-8 -*-


import calendar
import os
from django.core import signing
from django.core.signing import Signer
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from datetime import datetime
from  django.views.generic.dates import *
# Create your views here.
import sys
from Diplom.settings import BASE_DIR, MEDIA_ROOT, MEDIA_URL, STATIC_ROOT
from PlaningSystem.forms import UploadFileForm
from PlaningSystem.models import *
from dateutil import tz

# AdminsViews:
def checkAdmin(request):
    if not request.user.is_superuser:
        context = {
            'error': 'Доступ к этой странице ограничен!'
        }
        return render(request, 'PlaningSystem/admin/errors.html', context)
    return None

def autoSchelduleFill(request, workplace_id):
    t_start = datetime.datetime.now()
    since = get_since(request, 'awp')
    to = get_to(request, 'awp')
    workplace = Workplace.objects.get(id=workplace_id)
    shifts = workplace.schedule.getShiftsForPeriod(since, to)
    free_shifts = []
    for shift in shifts:
        if not shift.has_workers():
            free_shifts.append(shift)
    shifts = free_shifts
    users = workplace.getUsers()
    normal_weight = WishEnum.get_normal_weight()
    userShiftWeight = {}#user:shiftWeight
    shiftMaxWeight = {}#shift:[maxWeight,[users]]
    for user in users:
        shiftWeight = {} #shift:weight, shiftsNum: N , weightSum: S
        shiftWeight['shiftsNum'] = user.getShiftsNumForPeriod(since, to, workplace.schedule)
        shiftWeight['weightSum'] = 0
        shiftWeight['planing_shifts'] = []
        # print(user, user.getShiftsNumForPeriod(since, to, workplace.schedule))
        for shift in shifts:
            if shift.is_night() and not user.usersettings.nightShift:
                shiftWeight[shift] = None
                continue
            if shift in shiftMaxWeight:
                maxWeight = shiftMaxWeight[shift][0]
            else:
                maxWeight = None
                shiftMaxWeight[shift] = [maxWeight, []]
            # if shift.has_workers():
            #     shiftWeight[shift] = None
            # else:
            wishes = user.getWishForShift(shift)
            weight = 0
            if wishes.__len__() > 0:
                for wish in wishes:
                    if wish.wish != None:
                        weight += wish.wish.weight
                    else:
                        weight = normal_weight
            else:
                weight = normal_weight
            shiftWeight[shift] = weight
            shiftWeight['weightSum'] = shiftWeight['weightSum'] + weight
            if maxWeight == None:
                shiftMaxWeight[shift] = [weight, [user]]
            if maxWeight != None and maxWeight <= weight:
                if maxWeight == weight:
                    old_users = shiftMaxWeight[shift][1]
                    old_users.append(user)
                    shiftMaxWeight[shift] = [weight, old_users]
                else:
                    shiftMaxWeight[shift] = [weight, [user]]

        userShiftWeight[user] = shiftWeight
        # print(user, shiftWeight)
    # print(userShiftWeight)
    # print(shiftMaxWeight)
    planing_shifs = {}
    for shift in shifts:
        planing_shifs[shift] = None
        t_users = []
        if shiftMaxWeight[shift].__len__() > 1:
            t_users = shiftMaxWeight[shift][1]
        weight = shiftMaxWeight[shift][0]
        users_change = {}
        max_change = 0
        user_best_change = None
        print()
        print(shift.since.day,':',shift.since.hour, '-',shift.to.hour,',', shift.is_night(),sep='')
        for user in users:
            shiftWeight_for_user = userShiftWeight[user]
            k = user.could_work_at_shift(shift, shiftWeight_for_user['planing_shifts'])
            # print(shift.since, shift.is_night(), user, k)
            n = shiftWeight_for_user['shiftsNum']
            m = shiftWeight_for_user['weightSum']
            user_change = k*(n*normal_weight*2 + m)
            users_change[user] = user_change
            print(user,' ,can:', k,' ,Num:', n,' ,sum:', m,' ,change:', user_change,sep='')
            if user_change > max_change:
                max_change = user_change
                user_best_change = user
        print('postavle-', user_best_change)
        if user_best_change != None:
            # print(shift.since, user_best_change, users_change[user_best_change])
            shiftWeight_for_user = userShiftWeight[user_best_change]
            shiftWeight_for_user['shiftsNum'] -= 1
            shiftWeight_for_user['weightSum'] -= shiftWeight_for_user[shift]
            planing_shifs[shift] = user_best_change
            t_shifts = shiftWeight_for_user['planing_shifts']
            t_shifts.append(shift)
            shiftWeight_for_user['planing_shifts'] = t_shifts
            # print(user_best_change)
            # for sh in userShiftWeight[user_best_change]['planing_shifts']:
            #     print(sh.since)
            userShiftWeight[user_best_change] = shiftWeight_for_user
        # else:
        #     for user in users:
        #         user_best_change = None
        #         if user not in users_change:
        #             shiftWeight_for_user = userShiftWeight[user]
        #             k = user.could_work_at_shift(shift, shiftWeight_for_user['planing_shifts'])
        #             n = shiftWeight_for_user['shiftsNum']
        #             m = shiftWeight_for_user['weightSum']
        #             user_change = k*(n*normal_weight + m)
        #             users_change[user] = user_change
        #             if user_change > max_change:
        #                 max_change = user_change
        #                 user_best_change = user
        #     if user_best_change != None:
        #         planing_shifs[shift] = user_best_change
        #         t_shifts = shiftWeight_for_user['planing_shifts']
        #         t_shifts.append(shift)
        #         shiftWeight_for_user['planing_shifts'] = t_shifts
        #         userShiftWeight[user] = shiftWeight_for_user


    print(datetime.datetime.now() - t_start)
    for shift in shifts:
        user = planing_shifs[shift]
        if user!=None:
            wishes = user.getWishForShift(shift)
            if wishes.__len__()>0:
                for wish in wishes:
                    wish.isApproved = True
                    wish.save()
            else:
                wish = UserWish(since=shift.since, to=shift.to,isApproved=True,workingShift=shift, user=user)
                wish.save()
    # request.session['planing_shifts'] = planing_shifs
    return HttpResponseRedirect(reverse('workplaceAdmin', args=workplace_id))

def deletePlaningShifts(request, workplace_id):
    if 'planing_shifts' in request.session:
        planing_shifs = request.session['planing_shifts']
        for shift, user in planing_shifs:
            wishes = user.getWishForShift(shift)
            if wishes.__len__()>0:
                for wish in wishes:
                    wish.isApproved = False
                    wish.save()
        del request.session['planing_shifts']
    return HttpResponseRedirect(reverse('workplaceAdmin', args=workplace_id))

def activeUserAdmin(request):
    get_params = request.GET
    for name in get_params:
        value = get_params[name]
        if 'not_active_user' in name:
            value = int(value)
            user = User.objects.get(id=value)
            user.is_active = True
            user.save()
            Notification.UserSetActive(user)
        elif 'disactive_user' in name:
            value = int(value)
            user = User.objects.get(id=value)
            user.is_active = False
            user.save()

    return HttpResponseRedirect(reverse('admin'))

def admin(request):
    checkAdmin(request)
    not_active_users = User.objects.filter(is_active=False)
    all_workplaces = Workplace.objects.all()
    all_rates = Rate.objects.all()
    all_valid_users = User.getValidUsers()
    context = {
            'not_active_users': not_active_users,
            'all_workplaces': all_workplaces,
            'all_rates': all_rates,
            'all_valid_users': all_valid_users
        }
    if 'error' in request.session:
        context['error'] = request.session['error']
        del request.session['error']
    return render(request, 'PlaningSystem/admin/admin.html', context)

def workpalceAdminCreate(request):
    if 'name_wp' in request.GET:
        name = request.GET['name_wp']
        if name.__len__()<1:
            request.session['error'] ='Вы не ввели имя'
            return HttpResponseRedirect(reverse('admin'))
        wp = Workplace(name=name)
        wp.save()
        sh = Schedule(name='scheldue_'+name, workplace=wp)
        sh.save()
        return HttpResponseRedirect(reverse('workplaceAdmin', args=[wp.id]))
    else:
        request.session['error'] = 'Что-то пошло не так'
    return HttpResponseRedirect(reverse('admin'))

def workpalceAdmin(request, workplace_id):
    # users = User.getValidUsers()
    workplace = Workplace.objects.get(id=workplace_id)
    users = workplace.user_set.filter(is_active=True)
    scheldue = workplace.schedule
    rates = workplace.rates.all()
    since = get_since(request, 'wp')
    to = get_to(request, 'wp')
    days = GetDaysOfPeriod(since, to)
    ColomnNum = days.__len__() * QUANTUM.DAY + 1
    months = list_month_dur(since, to)
    shifts = scheldue.getShiftsForPeriod(since, to)
    shiftsDur = ShiftDuration.addDuratins(shifts, since, to)
    users_wishes = []
    # print(users)
    for user in users:
        uw = user.getUserWishesForWp(workplace, since, to)
        users_wishes.append(uw)
    context = {
        'workplace': workplace,
        'scheldue': scheldue,
        'users': users,
        'rates': rates,
        'since': since,
        'to': to,
        'shiftsDur': shiftsDur,
        'days': days,
        'users_wishes': users_wishes,
        'wishesEnum': WishEnum.objects.all(),
        'ColomnNum': ColomnNum,
        'months': months,
        'QUANT_FOR_SCHELDUE': QUANTUM.DAY
    }

    if 'planing_shifts' in request.session:
        context['has_delete'] = True

    return render(request, 'PlaningSystem/admin/workplace_admin.html', context)

def workplaceRatesAdmin(request, workplace_id):
    workplace = Workplace.objects.get(id=workplace_id)
    rates = Rate.objects.all()
    get_params = request.GET
    for name in get_params:
        value = get_params[name]
        if not 'of' in value:
            rate_id = int(value)
            rate = Rate.objects.get(id=rate_id)
            workplace.rates.add(rate)
            workplace.save()
        elif 'rate' in name:
            rate_id = int(name.replace('rate-', ''))
            rate = Rate.objects.get(id=rate_id)
            workplace.rates.remove(rate)
            workplace.save()
    rates_at_workplace = []
    for rate in rates:
        print(rate in workplace.rates.all())
        if rate in workplace.rates.all():
            rates_at_workplace.append([rate, True])
        else:
            rates_at_workplace.append([rate, False])
    # print(rates_at_workplace)
    context = {
        'workplace': workplace,
        'rates_at_workplace': rates_at_workplace,
    }
    return render(request, 'PlaningSystem/admin/workplace_rates.html', context)

def workplaceUsersAdmin(request, workplace_id):
    users = User.getValidUsers()
    workplace = Workplace.objects.get(id=workplace_id)
    get_params = request.GET
    for name in get_params:
        value = get_params[name]
        if not 'of' in value:
            user_id = int(value)
            user = User.objects.get(id=user_id)
            user.addWorkplace(workplace)
        elif 'user' in name:
            user_id = int(name.replace('user-', ''))
            user = User.objects.get(id=user_id)
            user.removeWorkplace(workplace)
    users_at_workplace = []
    for user in users:
        print(user in workplace.user_set.all())
        if user in workplace.user_set.all():
            users_at_workplace.append([user, True])
        else:
            users_at_workplace.append([user, False])
    context = {
        'workplace': workplace,
        'users_at_workplace': users_at_workplace,
    }
    return render(request, 'PlaningSystem/admin/users_at_workplace.html', context)

def workplaceChangeShiftAdmin(request, workplace_id):
    checkAdmin(request)
    get_params = request.GET
    workplace = Schedule.objects.get(id=workplace_id)
    url = "/PlaningSystem/workplace/admin/{!s}".format(workplace_id)
    for name in get_params:
        value = get_params[name]
        # print(name, value)
        # value = int(value)
        if 'user_wish' in name:
            wish_id = int(name.replace('user_wish-', ''))
            userWish = UserWish.objects.get(id=wish_id)
            if 'off' in value:
                if userWish.isApproved:
                    userWish.isApproved=False
                    Notification.ShiftDenied(userWish.user, userWish)
            else:
                if not userWish.isApproved:
                    userWish.isApproved=True
                    Notification.ShiftActived(userWish.user, userWish)
            userWish.save()
        elif 'shift-' in name:
            shift_id = int(name.replace('shift-', '').split('-')[0])
            if not 'off' in value:
                shift = WorkingShift.objects.get(id=shift_id)
                user_id = int(value)
                user = User.objects.get(id=user_id)
                wish = UserWish(since=shift.since, to=shift.to, isApproved=True, workingShift=shift, user=user)
                wish.save()
                Notification.ShiftActived(user, shift)
    return HttpResponseRedirect(url)

def scheldueChangeShiftAdmin(request, scheldue_id):
    checkAdmin(request)
    get_params = request.GET
    scheldue = Schedule.objects.get(id=scheldue_id)
    for name in get_params:
        value = get_params[name]
        if value.__len__()< 17:#КОСТЫЛЬ!!
            value = value + ':00'
        value = datetime.datetime.strptime(value,'%Y-%m-%dT%H:%M:%S')
        if 'since-shift_id' in name:
            shift_id = int(name.replace('since-shift_id-', ''))
            shift = WorkingShift.objects.get(id=shift_id)
            shift.since = value
            t_shift = WorkingShift.objects.get(id=shift_id)
            if shift.since>shift.to:
                request.session['scheldue_admin_error'] = "Смена кончается раньше чем начинается"
                continue
            if scheldue.isValidShifts([shift],t_shift):
                shift.save()
            else:
                request.session['scheldue_admin_error'] = "Параметр задан так что смены пересикаются"
        elif 'to-shift_id' in name:
            shift_id = int(name.replace('to-shift_id-', ''))
            shift = WorkingShift.objects.get(id=shift_id)
            shift.to = value
            t_shift = WorkingShift.objects.get(id=shift_id)
            if shift.since > shift.to:
                request.session['scheldue_admin_error'] = "Смена кончается раньше чем начинается"
                continue
            if scheldue.isValidShifts([shift], t_shift):
                shift.save()
            else:
                request.session['scheldue_admin_error'] = "Параметр задан так что смены пересикаются"
    return HttpResponseRedirect("/PlaningSystem/scheldue/admin/{!s}".format(scheldue_id))

def scheldueNewShiftAdmin(request, scheldue_id):
    checkAdmin(request)
    get_params = request.GET
    scheldue = Schedule.objects.get(id=scheldue_id)
    since = None
    to = None
    for name in get_params:
        value = get_params[name]
        if 'T' in value:
            value = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M')
            if 'since' in name:
                since = value
            elif 'to' in name:
                to = value
            if since!=None and to!=None:
                ws = WorkingShift(since=since, to=to, scheldue=scheldue)
                if scheldue.isValidShifts([ws]):
                    ws.save()
                else:
                    request.session['scheldue_admin_error'] = "Параметр задан так что смены пересикаются"

    return HttpResponseRedirect("/PlaningSystem/scheldue/admin/{!s}".format(scheldue_id))

def scheldueDeleteShiftAdmin(request, scheldue_id):
    checkAdmin(request)
    get_params = request.GET
    scheldue = Schedule.objects.get(id=scheldue_id)
    for name in get_params:
        if 'check_shift_id' in name:
            id = int(name.replace('check_shift_id-', ''))
            shift = WorkingShift.objects.get(id=id)
            shift.delete()
            if 'scheldue_admin_error' not in request.session:
                request.session['scheldue_admin_error'] = "Смены удалены"
    if 'scheldue_admin_error' not in request.session:
        request.session['scheldue_admin_error'] = "Нечего удалять"
    return HttpResponseRedirect(reverse('scheldueAdmin', args=[scheldue_id]))

def scheldueCopyShiftsAdmin(request, scheldue_id):
    checkAdmin(request)
    get_params = request.GET
    scheldue = Schedule.objects.get(id=scheldue_id)
    since = None
    to = None
    after = None
    for name in get_params:
        value = get_params[name]
        if 'T' in value:
            value = datetime.datetime.strptime(value,'%Y-%m-%dT%H:%M')
            if 'since' in name:
                since = value
            elif 'to' in name:
                to = value
            elif 'after' in name:
                after = value
            if since!=None and to!=None and after!=None:
                shifts = scheldue.getShiftsForPeriod(since,to)
                if scheldue.pasteShiftAfter(shifts,after):
                    request.session['scheldue_admin_error'] = "Скопированно!"
                else:
                    request.session['scheldue_admin_error'] = "Не скопированно! сменны где-то пересеклись"

    return HttpResponseRedirect("/PlaningSystem/scheldue/admin/{!s}".format(scheldue_id))

def scheldueGenerateShiftsAdmin(request, scheldue_id):
    checkAdmin(request)
    scheldue = Schedule.objects.get(id=scheldue_id)
    get_params = request.GET
    if 'after' in get_params and get_params['after']:
        after = datetime.datetime.strptime(get_params['after'], '%H:%M')
        after = datetime.timedelta(hours=after.hour, minutes=after.minute)
        print(after)
    else:
        request.session['scheldue_admin_error'] = "Укажите время начала смен"
        return HttpResponseRedirect(reverse('scheldueAdmin', args=[scheldue_id]))

    if 'shifts_num' in get_params and get_params['shifts_num']:
        shifts_num = int(get_params['shifts_num'])
        hours = int(24/shifts_num)
        hours = datetime.timedelta(hours=hours)
        print(hours)
    else:
        request.session['scheldue_admin_error'] = "Укажите количсвто смен в сутки"
        return HttpResponseRedirect(reverse('scheldueAdmin' ,args=[scheldue_id]))
    if 'set-month' in get_params:
        if 'month' in get_params and get_params['month']:
            month = get_params['month']
            month = datetime.datetime.strptime(month, '%Y-%m')
            since = datetime.datetime(month.year, month.month, 1)
            to = datetime.datetime(month.year, month.month, calendar.monthrange(month.year, month.month)[1])
            new_shifts = scheldue.generate_shifts(since, to, after, hours)
        else:
            request.session['scheldue_admin_error'] = "Месяц не задан"
            return HttpResponseRedirect(reverse('scheldueAdmin',args=[scheldue_id]))
    else:
        if 'since' in get_params and get_params['since']:
            since = datetime.datetime.strptime(get_params['since'], '%Y-%m-%d')
        else:
            request.session['scheldue_admin_error'] = "Не заданно время"
            return HttpResponseRedirect(reverse('scheldueAdmin',args=[scheldue_id]))
        if 'to' in get_params and get_params['to']:
            to = datetime.datetime.strptime(get_params['to'], '%Y-%m-%d')
        else:
            request.session['scheldue_admin_error'] = "Не заданно время"
            return HttpResponseRedirect(reverse('scheldueAdmin',args=[scheldue_id]))
        new_shifts = scheldue.generate_shifts(since, to, after, hours)
    if scheldue.isValidShifts(new_shifts):
        for shifts in new_shifts:
            shifts.save()
    else:
        request.session['scheldue_admin_error'] = "Новые смены пересикаются со старыми"
        return HttpResponseRedirect(reverse('scheldueAdmin',args=[scheldue_id]))
    return HttpResponseRedirect(reverse('scheldueAdmin',args=[scheldue_id]))

def scheldueAdmin(request, scheldue_id):
    checkAdmin(request)
    scheldue = Schedule.objects.get(id=scheldue_id)
    since = get_since(request, 'sh')
    to = get_to(request, 'sh')
    days = GetDaysOfPeriod(since, to)
    ColomnNum = days.__len__() * QUANTUM.DAY
    months = list_month_dur(since, to)
    shifts = scheldue.getShiftsForPeriod(since, to)
    durSh = ShiftDuration.addDuratins(shifts, since, to)
    error = None
    if "scheldue_admin_error" in request.session:
        error = request.session["scheldue_admin_error"]
        del request.session["scheldue_admin_error"]
    context = {
        'since': since,
        'to': to,
        'scheldue': scheldue,
        'scheldues': Schedule.objects.all(),
        'days': days,
        'ColomnNum': ColomnNum,
        'months': months,
        'DurWithSh': durSh,
        'error': error,
        'QUANT_FOR_SCHELDUE': QUANTUM.DAY

    }
    return render(request, 'PlaningSystem/admin/manage_working_shifts.html', context)


def rateChangeTCostAdmin(request, rate_id):
    checkAdmin(request)
    get_params = request.GET
    rate = Rate.objects.get(id=rate_id)
    for name in get_params:
        value = get_params[name]
        if 'since-id' in name:
            if value.__len__()< 17:#КОСТЫЛЬ!!
                value = value + ':00'
            value = datetime.datetime.strptime(value,'%Y-%m-%dT%H:%M:%S')
            timecost_id = int(name.replace('since-id-', ''))
            tcost = TimeCost.objects.get(id=timecost_id)
            tcost.since = value
            old_cost = TimeCost.objects.get(id=timecost_id)
            if tcost.since>tcost.to:
                request.session['scheldue_admin_error'] = "Ставка кончается раньше чем начинается"
                continue
            if rate.isValidTCosts([tcost], old_cost):
                tcost.save()
                request.session['scheldue_admin_error'] = "Сохранил"
            else:
                request.session['scheldue_admin_error'] = "Параметр задан так что ставки пересикаются"
        elif 'to-id' in name:
            if value.__len__()< 17:#КОСТЫЛЬ!!
                value = value + ':00'
            value = datetime.datetime.strptime(value,'%Y-%m-%dT%H:%M:%S')
            timecost_id = int(name.replace('to-id-', ''))
            tcost = TimeCost.objects.get(id=timecost_id)
            tcost.to = value
            old_cost = TimeCost.objects.get(id=timecost_id)
            if tcost.since > tcost.to:
                request.session['scheldue_admin_error'] = "ставка кончается раньше чем начинается"
                continue
            if rate.isValidTCosts([tcost], old_cost):
                tcost.save()
                request.session['scheldue_admin_error'] = "Сохранил"
            else:
                request.session['scheldue_admin_error'] = "Параметр задан так что ставки пересикаются"
        elif 'cost-id':
            value = float(value)
            timecost_id = int(name.replace('cost-id-', ''))
            tcost = TimeCost.objects.get(id=timecost_id)
            tcost.cost = value
            tcost.save()
            request.session['scheldue_admin_error'] = "Сохранил"

    return HttpResponseRedirect("/PlaningSystem/rate/admin/{!s}".format(rate_id))

def rateNewTCostAdmin(request, rate_id):
    checkAdmin(request)
    get_params = request.GET
    rate = Rate.objects.get(id=rate_id)
    since = None
    to = None
    cost = None
    for name in get_params:
        value = get_params[name]
        if 'T' in value:
            value = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M')
            if 'since' in name:
                since = value
            elif 'to' in name:
                to = value
        else:
            value = float(value)
            cost = value
        if since!=None and to!=None and cost!=None:
            ts = TimeCost(since=since, to=to, cost=cost, rate=rate)
            if rate.isValidTCosts([ts]):
                ts.save()
                request.session['scheldue_admin_error'] = "Добавлено"
            else:
                request.session['scheldue_admin_error'] = "Параметр задан так что смены пересикаются"

    return HttpResponseRedirect("/PlaningSystem/rate/admin/{!s}".format(rate_id))

def rateDeleteTCostAdmin(request, rate_id):
    checkAdmin(request)
    get_params = request.GET
    rate = Rate.objects.get(id=rate_id)
    for name in get_params:
        value = get_params[name]
        id = int(value)
        deleted = TimeCost.objects.get(id=id)
        deleted.delete()
        request.session['scheldue_admin_error'] = "Удалено"
    return HttpResponseRedirect("/PlaningSystem/rate/admin/{!s}".format(rate_id))

def rateCopyTCostAdmin(request, rate_id):
    checkAdmin(request)
    get_params = request.GET
    rate = Rate.objects.get(id=rate_id)
    since = None
    to = None
    after = None
    for name in get_params:
        value = get_params[name]
        if 'T' in value:
            value = datetime.datetime.strptime(value,'%Y-%m-%dT%H:%M')
            if 'since' in name:
                since = value
            elif 'to' in name:
                to = value
            elif 'after' in name:
                after = value
            if since!=None and to!=None and after!=None:
                tcosts = rate.getRateForPeriod(since,to)
                if rate.pasteTCostAfter(tcosts,after):
                    request.session['scheldue_admin_error'] = "Скопированно!"
                else:
                    request.session['scheldue_admin_error'] = "Не скопированно! сменны где-то пересеклись"

    return HttpResponseRedirect("/PlaningSystem/rate/admin/{!s}".format(rate_id))

def rateAdmin(request, rate_id):
    checkAdmin(request)
    rate = Rate.objects.get(id=rate_id)
    since = get_since(request, 'rt')
    to = get_to(request, 'rt')
    days = GetDaysOfPeriod(since, to)
    ColomnNum = days.__len__() * QUANTUM.DAY
    months = list_month_dur(since, to)
    costs = rate.getRateForPeriod(since, to)
    durSh = ShiftDuration.addDuratins(costs, since, to)
    error = None
    if "scheldue_admin_error" in request.session:
        error = request.session["scheldue_admin_error"]
        del request.session["scheldue_admin_error"]
    context = {
        'since': since,
        'to': to,
        'Rate': rate,
        'rates': Rate.objects.all(),
        'days': days,
        'ColomnNum': ColomnNum,
        'months': months,
        'DurWithRate': durSh,
        'error': error,
        'QUANT_FOR_SCHELDUE': QUANTUM.DAY

    }
    return render(request, 'PlaningSystem/admin/manage_rate.html', context)

#/////////////////////////////////////////////end admin
def index(request):
    print(
        STATIC_ROOT
    )
    if request.user.is_authenticated():
        print(request.user.is_superuser)
        if request.user.is_superuser:
            print(reverse('admin'))
            return HttpResponseRedirect(reverse('admin'))
        else:
            return HttpResponseRedirect(reverse('user', args=[request.user.id]))
    return render(request, 'PlaningSystem/index.html')

def password_reset(request):
    users = []
    if 'email' in request.POST and request.POST['email']:
        users = User.objects.filter(email=request.POST['email'])
        if users.__len__()<1:
            return render(request, 'PlaningSystem/password_reset.html', {'error': "По указанному email, ничего не найдено"})
    elif 'username' in request.POST and request.POST['username']:
        users = User.objects.filter(username=request.POST['username'])
        if users.__len__()<1:
            return render(request, 'PlaningSystem/password_reset.html', {'error': "По указанному логину, ничего не найдено"})
    for user in users:
        signer = Signer(salt='extra')
        key = signer.sign(user.id)
        text = 'Здрасвуйте, ' + user.getFIO() + ', для востановления пароля перейдите по ссылке:\n'
        text += 'http://' + request.META['HTTP_HOST']+reverse('password_reset_confirm') + '?key=' + key
        text += '\n\n Это письмо сгенерировано автоматически на него не нужно отвечать'
        send_mail('Востановление пароля', text, EMAIL_HOST_USER, [user.email])
        context = {
            'messege': 'Вам было высланно письмо',
        }
        return render(request, 'PlaningSystem/password_reset.html', context)
    return render(request, 'PlaningSystem/password_reset.html')

def password_reset_confirm(request):
    if 'key' in request.GET:
        key = request.GET['key']
        try:
            signer = Signer(salt='extra')
            user_id = signer.unsign(key)
        except signing.BadSignature:
            return render(request, 'PlaningSystem/password_reset_confirm.html', {'error': "Неверный URL"})
        user = User.objects.filter(id=user_id)
        if user.count() == 1:
            user = user[0]
        else:
            return render(request, 'PlaningSystem/password_reset_confirm.html', {'error': "Пользователь не найден"})
    else:
        return render(request, 'PlaningSystem/password_reset_confirm.html', {'error': "Неверный URL"})

    pass1 = None
    pass2 = None
    context = {
        'pass_user': user
    }
    if 'password1' in request.POST and request.POST['password1']:
        pass1 = request.POST['password1']
    if 'password2' in request.POST and request.POST['password2']:
        pass2 = request.POST['password2']
    if pass1 == pass2 is not None:
        user.set_password(pass1)
        context['message'] = 'Пароль изменен'
        user.save()
    if pass1 != pass2:
        context['message'] = 'Пароли не совпадают'

    return render(request, 'PlaningSystem/password_reset_confirm.html', context)

def register_user(request):
    error = ''
    username = None
    password1 = None
    password2 = None
    email = None
    first_name = None
    second_name = None
    third_name = None
    mobile_phone = None
    work_phone = None
    avatar = None
    print(request.FILES)
    if 'username' in request.POST:
        username = request.POST['username']
        if not username:
            return render(request, 'PlaningSystem/registration.html', {'error': 'введите логин'})
    if 'password1' in request.POST:
        password1 = request.POST['password1']
        if not password1:
            return render(request, 'PlaningSystem/registration.html', {'error': 'введите пароль'})
    if 'password2' in request.POST:
        password2 = request.POST['password2']
        if not password2:
            return render(request, 'PlaningSystem/registration.html', {'error': 'подтвердите пароль'})
        if password1!=password2:
            return render(request, 'PlaningSystem/registration.html', {'error': 'пароли не совпадат'})
    if 'email' in request.POST:
        email = request.POST['email']
        if not email:
            return render(request, 'PlaningSystem/registration.html', {'error': 'введите email'})
    if 'first_name' in request.POST:
        first_name = request.POST['first_name']
        if not first_name:
            return render(request, 'PlaningSystem/registration.html', {'error': 'введите имя'})
    if 'second_name' in request.POST:
        second_name = request.POST['second_name']
        if not second_name:
            return render(request, 'PlaningSystem/registration.html', {'error': 'введите фамилию'})
    new_user = None
    if User.objects.filter(username=username):
        return render(request, 'PlaningSystem/registration.html', {'error':'логин занят'})
    else:
        if username!=None and first_name!=None and second_name!=None and email!=None and password1!=None:
            print('user created')
            new_user = User(username=username,first_name=first_name,last_name=second_name,email=email,password='',is_active=False)
            new_user.set_password(password1)
    if 'third_name' in request.POST:
        third_name = request.POST['third_name']
        new_user.third_name = third_name
    if 'mobile_phone' in request.POST:
        mobile_phone = request.POST['mobile_phone']
        new_user.mobile_phone = mobile_phone
    if 'work_phone' in request.POST:
        work_phone = request.POST['work_phone']
        new_user.work_phone = work_phone
    if 'avatar' in request.FILES:
        avatar = request.FILES['avatar']
        print("ava")
        new_user.avatar = avatar
    if new_user is not None:
        new_user.save()
        settings = UserSettings()
        settings.user = new_user
        settings.save()
        Notification.NewUserRegistered(new_user)
        return HttpResponseRedirect(reverse('user', args=[new_user.id]))
    context = {
    }
    return render(request, 'PlaningSystem/registration.html', context)

def userWishSave(request):
    get_params = request.GET
    for name in get_params:
        value = int(get_params[name])
        value = WishEnum.objects.get(id=value)
        print(value)
        # print(name,value)
        if 'wish_id' in name:
            wish_id = int(name.replace('wish_id-', ''))
            # print(wish_id)
            userWish = UserWish.objects.get(id=wish_id)
            userWish.wish = value
            userWish.isApproved = False
            if request.user.id == userWish.user.id:
                userWish.save()
        elif 'shift_id' in name:
            shift_id = int(name.replace('shift_id-', ''))
            shift = WorkingShift.objects.get(id=shift_id)
            uw = UserWish(since=shift.since,to=shift.to,wish=value,isApproved=False,workingShift=shift,user=request.user)
            uw.save()
    return HttpResponseRedirect(reverse('user',args=[request.user.id]))

def changeUser(request, user_id):
    user = request.user
    if user.is_anonymous():
        return HttpResponseNotFound('<h2>У вас нет прав для просмотра этой страницы, зарегестрируйтесь или войдите</h2>')
    if not user.is_superuser and user.id != int(user_id):
        return HttpResponseNotFound('<h2>Вы не можете редоктировать эту страницу</h2>')
    if user.is_authenticated and user.id == int(user_id):
        ch_user = User.objects.get(id=user_id)
        context = {
            'ch_user': ch_user
        }
        if 'error' in request.session:
            context['error'] = request.session['error']
            del request.session['error']
        if 'error_pas' in request.session:
            context['error_pas'] = request.session['error_pas']
            del request.session['error_pas']
        return render(request,'PlaningSystem/change_user.html', context)
    if user.is_superuser:
        return HttpResponseRedirect(reverse('admin:PlaningSystem_user_change',args=[user_id]))


def notificationsUser(request):
    user = request.user
    if user.is_authenticated:
        notices = (Notification.objects.filter(user=user)).order_by('-pub_date')
    else:
        return HttpResponseRedirect(reverse('index'))

    new_notices = []
    old_notices = []
    counter = 0
    for note in notices:
        if counter>100:
            break
        else:
            if note.page == True:
                old_notices.append(note)
            elif note.page == False:
                new_notices.append(note)
                note.page = True
                note.save()
            counter+=1
    context = {
        'notices': notices,
        'old_notices': old_notices,
        'new_notices': new_notices,
    }
    return render(request, 'PlaningSystem/notifications.html', context)

def saveChangeUser(request):
    ch_user = request.user
    username = None
    password1 = None
    password2 = None
    email = None
    first_name = None
    second_name = None
    third_name = None
    mobile_phone = None
    work_phone = None
    avatar = None
    if 'username' in request.POST:
        username = request.POST['username']
        if not username:
            request.session['error'] = 'логин не может быть пустым'
            return HttpResponseRedirect(reverse('changeUser', args=[ch_user.id]))
        for us in User.objects.filter(username=username):
            if us.id != ch_user.id:
                request.session['error'] = 'логин уже занят'
                return HttpResponseRedirect(reverse('changeUser', args=[ch_user.id]))

    if 'password1' in request.POST:
        password1 = request.POST['password1']
        if not password1:
            request.session['error_pas'] = 'пустой пароль, это как?'
            return HttpResponseRedirect(reverse('changeUser', args=[ch_user.id]))
    if 'password2' in request.POST:
        password2 = request.POST['password2']
        if not password2:
            request.session['error_pas'] = 'а подтвердить?'
            return HttpResponseRedirect(reverse('changeUser', args=[ch_user.id]))
        if password1!=password2:
            request.session['error_pas'] = 'пароли не совпадат'
            return HttpResponseRedirect(reverse('changeUser', args=[ch_user.id]))
        else:
            ch_user.set_password(password1)
    if 'email' in request.POST:
        email = request.POST['email']
    if 'first_name' in request.POST:
        first_name = request.POST['first_name']
    if 'second_name' in request.POST:
        second_name = request.POST['second_name']
    if 'third_name' in request.POST:
        third_name = request.POST['third_name']
    if 'mobile_phone' in request.POST:
        mobile_phone = request.POST['mobile_phone']
    if 'work_phone' in request.POST:
        work_phone = request.POST['work_phone']

    if 'avatar' in request.FILES:
        avatar = request.FILES['avatar']
        ch_user.avatar = avatar
    if username != None and username.__len__()>0:
        ch_user.username = username
    if email != None and email.__len__()>0:
        ch_user.email = email
    if first_name != None and first_name.__len__()>0:
        ch_user.first_name = first_name
    if second_name != None and second_name.__len__()>0:
        ch_user.last_name = second_name
    if third_name != None and username.__len__()>0:
        ch_user.third_name = third_name
    if mobile_phone != None and username.__len__()>0:
        ch_user.mobile_phone = mobile_phone
    if work_phone != None and username.__len__()>0:
        ch_user.work_phone = work_phone
    ch_user.save()
    return HttpResponseRedirect(reverse('changeUser', args=[request.user.id]))

def user(request, user_id):
    user = request.user
    if user.is_authenticated and user.id == int(user_id):
        if user.is_superuser:
            return HttpResponseRedirect(reverse('admin'))
        return my_page(request, user_id)
    else:
        viewed_user = User.objects.get(id=user_id)
        if not viewed_user in User.getValidUsers():
            return HttpResponseNotFound('<h1>Пользватель не найден или отключен</h1>')
        since = get_since(request,'user')
        to = get_to(request,'user')
        days = GetDaysOfPeriod(since, to)
        ColomnNum = days.__len__() * QUANTUM.DAY + 1
        months = list_month_dur(since, to)
        wishes = viewed_user.getUserWishes(since, to)
        workplaces = viewed_user.getWorkPlaces()
        context = {
            'since': since,
            'to': to,
            'user': User.objects.get(id=user_id),
            'days': days,
            'workplaces': workplaces,
            'wishes': wishes,
            'wishesEnum': WishEnum.objects.all(),
            'ColomnNum': ColomnNum,
            'months': months,
            'QUANT_FOR_SCHELDUE': QUANTUM.DAY
        }
        return render(request, 'PlaningSystem/user.html', context)

def my_page(request, user_id):
    viewed_user = User.objects.get(id=user_id)
    since = get_since(request,'user')
    to = get_to(request,'user')
    days = GetDaysOfPeriod(since, to)
    ColomnNum = days.__len__() * QUANTUM.DAY + 1
    months = list_month_dur(since, to)
    wishes = viewed_user.getUserWishes(since, to)
    workplaces = viewed_user.getWorkPlaces()
    context = {
        'since': since,
        'to': to,
        'user': User.objects.get(id=user_id),
        'days': days,
        'workplaces': workplaces,
        'wishes': wishes,
        'wishesEnum': WishEnum.objects.all(),
        'ColomnNum': ColomnNum,
        'months': months,
        'QUANT_FOR_SCHELDUE': QUANTUM.DAY
    }
    return render(request, 'PlaningSystem/my_page.html', context)

def rate(request, rate_id):
    rate = Rate.objects.get(id=rate_id)
    timeCosts = rate.getRate()
    times=[]
    costs=[]
    for timeCost in timeCosts:
        times.append(timeCost.since.strftime("%Y-%m-%d %H:%M:%S - ") + timeCost.since.strftime("%d %H:%M:%S"))
        costs.append(timeCost.cost)
    context = {
        'rate': rate,
        # 'timeCosts': timeCosts,
        'times': times,
        'costs': costs
    }
    return render(request, 'PlaningSystem/rate.html', context)

def workplace(request, workplace_id):
    workplace = Workplace.objects.get(id=workplace_id)
    scheldue = workplace.schedule
    rates = workplace.rates.all()
    viewing_user = request.user
    if viewing_user.is_anonymous():
        return HttpResponseNotFound('<h2>У вас нет прав для просмотра этой страницы, зарегестрируйтесь или войдите</h2>')
    if not viewing_user in User.getValidUsers():
        return HttpResponseNotFound('<h2>У вас нет прав для просмотра этой страницы</h2>')
    users = User.getValidUsers([viewing_user])
    since = get_since(request,'u_wp')
    to = get_to(request,'u_wp')
    days = GetDaysOfPeriod(since, to)
    ColomnNum = days.__len__() * QUANTUM.DAY + 1
    months = list_month_dur(since, to)
    shifts = scheldue.getShiftsForPeriod(since, to)
    shiftsDur = ShiftDuration.addDuratins(shifts, since, to)
    viewing_user_wishes = viewing_user.getUserWishesForWp(workplace,since, to)
    users_wishes = []
    for user in users:
        uw = user.getUserWishesForWp(workplace,since, to)
        users_wishes.append(uw)
    context = {
        'workplace': workplace,
        'users': users,
        'rates': rates,
        'since': since,
        'to': to,
        'shiftsDur': shiftsDur,
        'viewing_user': viewing_user,
        'viewing_user_wishes': viewing_user_wishes,
        'days': days,
        'users_wishes': users_wishes,
        'wishesEnum': WishEnum.objects.all(),
        'ColomnNum': ColomnNum,
        'months': months,
        'QUANT_FOR_SCHELDUE': QUANTUM.DAY
    }
    return render(request, 'PlaningSystem/workplace.html', context)


def userShedule(request, user_id):
    user = User.objects.get(id=user_id)
    wishes = UserWish.objects.filter(user=user)
    periodDays = GetDaysOfMont(datetime.datetime(2013, 12, 5))
    tableItems = []
    workplaces = user.getWorkPlaces()
    for workplace in workplaces:
        workplaceitems = [workplace.name]
        for day in periodDays:
            workplaceitems.append(user.getWishForDate(day, workplace))
        tableItems.append(workplaceitems)

    wishesEnum = WishEnum.objects.all()
    context = {
        'user': user,
        'wishes': wishes,
        'head':  periodDays,
        'items': tableItems,
        'wishesEnum': wishesEnum
    }
    return render(request, 'PlaningSystem/shedule.html', context)

def userSheduleAdd(request):

    context = {
        'user': user,

    }
    return render(request, 'PlaningSystem/shedule.html', context)

def GetDaysOfMont(dateTime):

    month = dateTime.month
    year = dateTime.year
    num = calendar.monthrange(year, month)[1]
    set = []
    for i in range(1, num+1):
        set.append(datetime.date(year, month, i))

    return set

def GetDaysOfPeriod(since, to):
    set = []
    num = (to - since).days + 1
    # print(since,to,num)
    for i in range(0, num, 1):
        set.append(since + datetime.timedelta(days=i))
    return set

def list_month_dur(since, to):
    num_of_months = (to.year - since.year)*12 + to.month - since.month
    months = []
    for i in range(0, num_of_months+1, 1):
        month = add_months(since, i)
        dur = calendar.monthrange(month.year, month.month)[1]*QUANTUM.DAY
        if since.month == month.month and since.year == month.year:
            dur = dur  - (since.day - 1)*QUANTUM.DAY
        if to.month == month.month and to.year == month.year:
            dur = dur - (calendar.monthrange(month.year, month.month)[1] - to.day)*QUANTUM.DAY
        months.append([month, dur])
    return months

def login(request):
    #sys.stdout.write("asd\n")

    if request.method == 'POST':
        post = request.POST
        password = post.__getitem__('password')
        username = post.__getitem__('username')
        users = User.objects.filter(name=username)
        sys.stdout.write(username + "\n")
        for user in users:
            sys.stdout.write("asd\n")
            if user.password == password:
                return render(request, 'PlaningSystem/index.html')
    context = {
        'message': "wrong password or username",

    }
    return render(request, 'PlaningSystem/login.html', context)

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + round(month/12)
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year,month,day)

def get_since(request,key):
    today = datetime.date.today()
    since = datetime.datetime(today.year, today.month, 1)
    if 'since' in request.GET:
        since = datetime.datetime.strptime(request.GET['since'], '%Y-%m-%d')
    elif 'since_'+key in request.session:
        since = datetime.datetime.strptime(request.session['since_'+key], '%Y-%m-%d')
    request.session['since_'+key] = since.strftime('%Y-%m-%d')
    return since

def get_to(request, key):
    today = datetime.date.today()
    to = datetime.datetime(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    if 'to' in request.GET:
        to = datetime.datetime.strptime(request.GET['to'], '%Y-%m-%d')
    elif 'to_'+key in request.session:
        to = datetime.datetime.strptime(request.session['to_'+key], '%Y-%m-%d')
    to += datetime.timedelta(hours=23, minutes=59)
    request.session['to_'+key] = to.strftime('%Y-%m-%d')
    return to



#############
def handle_uploaded_file(f):
    with open(MEDIA_ROOT + MEDIA_URL + f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def test(request):

    if request.method == 'POST':
        print(request.FILES)
        form = UploadFileForm(request.POST, request.FILES)
        # print(form)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])

    else:
        form = UploadFileForm()
    context = {
        'form': form,

    }
    return render(request, 'PlaningSystem/test.html', context)