import calendar
import os
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from datetime import datetime
from  django.views.generic.dates import *
# Create your views here.
import sys
from Diplom.settings import BASE_DIR, MEDIA_ROOT, MEDIA_URL
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
    return render(request, 'PlaningSystem/admin/admin.html', context)

def workpalceAdmin(request, workplace_id):
    users = User.getValidUsers()
    workplace = Workplace.objects.get(id=workplace_id)
    scheldue = workplace.schedule
    rates = workplace.rates.all()
    today = datetime.date.today()
    since = datetime.datetime(today.year, today.month, 1)
    to = datetime.datetime(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    if request.GET.get('since'):
        since = datetime.datetime.strptime(request.GET['since'], '%Y-%m-%d')
    elif request.session['since']:
        since = datetime.datetime.strptime(request.session['since'], '%Y-%m-%d')
    if request.GET.get('to'):
        to = datetime.datetime.strptime(request.GET['to'], '%Y-%m-%d')
    elif request.session['to']:
        to = datetime.datetime.strptime(request.session['to'], '%Y-%m-%d')
    request.session['since'] = since.strftime('%Y-%m-%d')
    request.session['to'] = to.strftime('%Y-%m-%d')
    to += datetime.timedelta(hours=23, minutes=59)
    days = GetDaysOfPeriod(since, to)
    ColomnNum = days.__len__() * QUANTUM.DAY + 1
    months = list_month_dur(since, to)
    shifts = scheldue.getShiftsForPeriod(since, to)
    shiftsDur = ShiftDuration.addDuratins(shifts, since, to)
    users_wishes = []
    print(users)
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
                userWish.isApproved=False
            else:
               userWish.isApproved=True
            userWish.save()
        elif 'shift-' in name:
            shift_id = int(name.replace('shift-', ''))
            if not 'off' in value:
                shift = WorkingShift.objects.get(id=shift_id)
                user_id = int(value)
                user = User.objects.get(id=user_id)
                wish = UserWish(since=shift.since, to=shift.to, isApproved=True, wish=WishEnum.objects.get(id=1), workingShift=shift, user=user)
                wish.save()
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
    since = None
    to = None
    for name in get_params:
        value = get_params[name]
        if 'T' in value:
            if value.__len__()< 17:#КОСТЫЛЬ!!
                value = value + ':00'
            value = datetime.datetime.strptime(value,'%Y-%m-%dT%H:%M:%S')
            if 'since' in name:
                since = value
            elif 'to' in name:
                to = value
            if since!=None and to!=None:
                shifts = scheldue.getShiftsForPeriod(since, to)
                if shifts.__len__()>0 and shifts[0].since==since and shifts[0].to==to:
                    shifts[0].deleteWithUserWishes()
                    request.session['scheldue_admin_error'] = "Удалено!"
                else:
                    request.session['scheldue_admin_error'] = "Не получилось!"

    return HttpResponseRedirect("/PlaningSystem/scheldue/admin/{!s}".format(scheldue_id))

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

def scheldueAdmin(request, scheldue_id):
    checkAdmin(request)
    scheldue = Schedule.objects.get(id=scheldue_id)
    today = datetime.date.today()
    if request.GET.get('since'):
        since = datetime.datetime.strptime(request.GET['since'], '%Y-%m-%d')
    else:
        since = datetime.datetime(today.year, today.month, 1)
    if request.GET.get('to'):
        to = datetime.datetime.strptime(request.GET['to'], '%Y-%m-%d')
    else:
        to = datetime.datetime(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    to += datetime.timedelta(hours=23, minutes=59)
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
    today = datetime.date.today()
    if request.GET.get('since'):
        since = datetime.datetime.strptime(request.GET['since'], '%Y-%m-%d')
    else:
        since = datetime.datetime(today.year, today.month, 1)
    if request.GET.get('to'):
        to = datetime.datetime.strptime(request.GET['to'], '%Y-%m-%d')
    else:
        to = datetime.datetime(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    to += datetime.timedelta(hours=23, minutes=59)
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
    context = {
        'users': User.objects.all(),
        'workplaces': Workplace.objects.all(),
        'rates': Rate.objects.all(),
        'scheldues': Schedule.objects.all()
    }
    return render(request, 'PlaningSystem/index.html', context)

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
    context = {
    }
    return render(request, 'PlaningSystem/registration.html', context)

def userSave(request):
    get_params = request.GET
    for name in get_params:
        value = int(get_params[name])
        value = WishEnum.objects.get(id=value)
        # print(value)
        # print(name,value)
        if 'wish_id' in name:
            wish_id = int(name.replace('wish_id-', ''))
            # print(wish_id)
            userWish = UserWish.objects.get(id=wish_id)
            userWish.wish = value
            userWish.save()
        elif 'shift_id' in name:
            shift_id = int(name.replace('shift_id-', ''))
            shift = WorkingShift.objects.get(id=shift_id)
            uw = UserWish(since=shift.since,to=shift.to,wish=value,isApproved=False,workingShift=shift,user=request.user)
            uw.save()
            # print('shift:', wish_id)

    return HttpResponseRedirect("/PlaningSystem/user/{!s}".format(request.user.id))

def user(request, user_id):
    logined_user = request.user
    viewed_user = User.objects.get(id=user_id)
    today = datetime.date.today()
    since = datetime.datetime(today.year, today.month, 1)
    to = datetime.datetime(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    # from_zone = tz.tzutc()
    if request.GET.get('since'):
        since = datetime.datetime.strptime(request.GET['since'], '%Y-%m-%d')
        # tzinfo=None
        # print(since.tzinfo)
        # since.replace(tzinfo=locals())
    if request.GET.get('to'):
        to = datetime.datetime.strptime(request.GET['to'], '%Y-%m-%d')
        # to.replace(tzinfo=from_zone)
    to += datetime.timedelta(hours=23, minutes=59)
    days = GetDaysOfPeriod(since, to)
    ColomnNum = days.__len__() * QUANTUM.DAY + 1
    months = list_month_dur(since, to)
    # wishes = viewed_user.getUserWishesforPeriod(since, to)
    wishes = viewed_user.getUserWishes(since, to)
    workplaces = viewed_user.getWorkPlaces()
    # for workplace in workplaces:
    #     workplaceitems = [workplace]
    #     for day in days:
    #         workplaceitems.append(viewed_user.getWishForDate(day, workplace))
    #     wishes.append(workplaceitems)
    context = {
        'since': since,
        'to': to,
        'user': User.objects.get(id=user_id),
        'days': days,
        'workplaces': workplaces,
        'wishes': wishes,
        # 'wishes': [],
        'wishesEnum': WishEnum.objects.all(),
        'ColomnNum': ColomnNum,
        'months': months,
        'QUANT_FOR_SCHELDUE': QUANTUM.DAY
    }
    return render(request, 'PlaningSystem/user.html', context)

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
    # users = User.objects.filter(workplaces=workplace).exclude(id=viewing_user.id)
    users = User.getValidUsers([viewing_user])
    today = datetime.date.today()
    since = datetime.datetime(today.year, today.month, 1)
    to = datetime.datetime(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    # from_zone = tz.tzutc()
    if request.GET.get('since'):
        since = datetime.datetime.strptime(request.GET['since'], '%Y-%m-%d')
        # tzinfo=None
        # print(since.tzinfo)
        # since.replace(tzinfo=locals())
    if request.GET.get('to'):
        to = datetime.datetime.strptime(request.GET['to'], '%Y-%m-%d')
        # to.replace(tzinfo=from_zone)
    to += datetime.timedelta(hours=23, minutes=59)
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
    print(users_wishes)
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