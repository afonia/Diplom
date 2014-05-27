#!/usr/bin/env python
# -*- coding: utf-8 -*-

import calendar
import datetime
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.mail import send_mail
from django.db import models
from PIL import Image

from django.utils.timezone import override


# class MY_CONST(object):
#     MINUTES_IN_DAY = 1440
#     HOURS_IN_DAY = 24
#     MINUTES_IN_HOUR = 60
#     QUANT_FOR_SCHELDUE = HOURS_IN_DAY
#     QUANT_OF_TIME = MINUTES_IN_HOUR
from Diplom.settings import EMAIL_HOST_USER


class QUANTUM(object):
    QUANTUM_IS_SECOND = 1
    QUANTUM_IS_MINUTE = 1 / 60
    QUANTUM_IS_HOUR = 1 / 3600
    QUANTUM_IS_DAY = 1 / 86400
    DEF_QUANTUM = QUANTUM_IS_HOUR
    DAY = 86400 * DEF_QUANTUM
    HOUR = 3600 * DEF_QUANTUM
    MINUTE = 60 * DEF_QUANTUM
    SECOND = 1 * DEF_QUANTUM
    IN_SECONDS = 1/DEF_QUANTUM

class SHIFT_PLANING_SETTINGS(object):
    DAYS_AFTER_NIGHT_SHIFT = 1
    DAYS_AFTER_DAY_SHIFT = 2
    MAX_SECONDS_BETWEN_SHIFTS = 3600
    SECONDS_AFTER_NIGHT_SHIFT = DAYS_AFTER_NIGHT_SHIFT * 86400
    SECONDS_AFTER_DAY_SHIFT = DAYS_AFTER_DAY_SHIFT * 86400


class ShiftDuration(object):
    def __init__(self, dur, hasShift):
        self.duration = dur
        self.hasShift = hasShift

    @staticmethod
    def addDuratins(shifts, startDate, endDate):
        shifts_list = list(shifts)
        DurShift = []
        tz = None
        # delta_err = 0
        if shifts_list.__len__() > 0:
            tz = shifts_list[0].since.tzinfo
            delta = (shifts_list[0].since - startDate.replace(tzinfo=tz)).total_seconds()
            num = round(delta*QUANTUM.SECOND,0)
            if num >= 1:
                DurShift.append([ShiftDuration(num, False)])
        for shift in shifts_list:
            # print(shift.since, shift.to)
            tz = shift.since.tzinfo
            index = shifts_list.index(shift)
            delta = (shift.to - shift.since).total_seconds()
            num = round(delta*QUANTUM.SECOND,0)
            DurShift.append([ShiftDuration(num, True), shift])
            if index != shifts_list.__len__() - 1:
                delta = abs((shifts_list[index + 1].since - shift.to).total_seconds())
                num = round(delta*QUANTUM.SECOND,0)
                if num >= 1:
                    DurShift.append([ShiftDuration(num, False)])
            else:
                delta = (endDate.replace(tzinfo=tz) - shift.to).total_seconds()
                # print(endDate)
                num = round(delta*QUANTUM.SECOND,0)
                if num >= 1:
                    DurShift.append([ShiftDuration(num * QUANTUM.SECOND, False)])
        return DurShift

CHOICES_NOTIFICATION = (
    (None, "Не высылать"),
    (True, "Выслано"),
    (False, "Будет выслано")
)

CHOICES_SHIFT_NIGHT = (
    (True, "Может дежурить ночью"),
    (False, "Заступает на смены только днем")
)
CHOICES_SHIFT_24DAY = (
    (True, "Может дежурить сутки"),
    (False, "Заступает на смены не длинее суток")
)

class Rate(models.Model):
    name = models.CharField(max_length=300)
    # quantumTimeCost = models.TimeField() #можно изменить на datetime тогда квант станет больше
    #pub_date = models.DateTimeField('date published')

    # @property
    def getRate(self):
        return self.timecost_set.all()

    def getRateForPeriod(self, startDate, endDate):
        return self.timecost_set.filter(since__range=[startDate, endDate]).order_by('since')

    def isValidTCosts(self, timeCosts, exeptCost=None):
        # shifts = shifts.order_by('since')
        allCosts = self.getRate() #тут можно брать за период
        # allshift = list(allshift)
        for shift in timeCosts:
            for workSh in allCosts:
                if exeptCost != None and workSh.id == exeptCost.id:
                    continue
                if workSh.since < shift.since < workSh.to:
                    return False
                if workSh.since < shift.to < workSh.to:
                    return False
                if shift.since < workSh.since < shift.to:
                    return False
                if shift.since < workSh.to < shift.to:
                    return False

        return True

    def pasteTCostAfter(self, tcosts, after):
        # shifts = self.getShiftsForPeriod(after,after)
        new_tcosts = []
        if tcosts.__len__() > 0:
            delta = after - tcosts[0].since
            for tc in tcosts:
                ws = TimeCost(since=tc.since + delta, to=tc.to + delta, cost=tc.cost, rate=self)
                new_tcosts.append(ws)
            if self.isValidTCosts(new_tcosts):
                for tc in new_tcosts:
                    tc.save()
                return True
            else:
                return False

    def __unicode__(self):
        return self.name


class TimeCost(models.Model):
    since = models.DateTimeField()
    to = models.DateTimeField()
    cost = models.FloatField()
    rate = models.ForeignKey(Rate)
    #pub_date = models.DateTimeField('date published')
    # def __init__(self, since, to, cost, rate):
    #     self.since = since
    #     self.to = to
    #     self.cost = cost
    #     self.rate = rate

    # def __unicode__(self):
    #     return self.since + "-" + self.to


class WishEnum(models.Model):
    wish = models.CharField(max_length=300)
    image = models.ImageField(upload_to='media/wish', blank=True, max_length=1000, null=True, default='')
    weight = models.FloatField(blank=True, null=True, default=0)
    #pub_date = models.DateTimeField('date published')

    def __unicode__(self):
        return self.wish
    @staticmethod
    def get_normal_weight():
        wishes = WishEnum.objects.all()
        max = wishes[0].weight
        min = max
        for wish in wishes:
            if max < wish.weight:
                max = wish.weight
            if min > wish.weight:
                min = wish.weight
        return (max - min)/2

class Workplace(models.Model):
    name = models.CharField(max_length=300)
    rates = models.ManyToManyField(Rate, blank=True, null=True)
    #pub_date = models.DateTimeField('date published')

    @property
    def getSchedule(self):
        return Schedule.objects.get(workplace=self)

    def getUsers(self):
        return self.user_set.filter(is_active=True)

    def __unicode__(self):
        return self.name


class Schedule(models.Model):
    name = models.CharField(max_length=300)
    workplace = models.OneToOneField(Workplace, blank=True, null=True)
    #pub_date = models.DateTimeField('date published')

    @property
    def getSchedule(self):
        return self.userwish_set.all().order_by('since')

    def getScheduleForUser(self, user):
        return self.userwish_set.get(user=user)

    def getShifts(self):
        return self.workingshift_set.all()

    def getShiftsForPeriod(self, startDate, endDate):
        return self.workingshift_set.filter(since__range=[startDate, endDate]).order_by('since')

    def isValidShifts(self, shifts, exeptShift=None):
        # shifts = shifts.order_by('since')
        allshift = self.getShifts() #тут можно брать за период
        # allshift = list(allshift)
        for shift in shifts:
            for workSh in allshift:
                if exeptShift != None and workSh.id == exeptShift.id:
                    continue
                if workSh.since < shift.since < workSh.to:
                    return False
                if workSh.since < shift.to < workSh.to:
                    return False
                if shift.since < workSh.since < shift.to:
                    return False
                if shift.since < workSh.to < shift.to:
                    return False

        return True

    def generate_shifts(self, startDate, endDate, startTime, hours_in_shift):
        shifts_list = []
        current_date = startDate + startTime
        endDate = endDate + datetime.timedelta(days=1)
        while(current_date+hours_in_shift<=endDate):
            shift = WorkingShift(since=current_date, to=(current_date + hours_in_shift), scheldue=self)
            current_date = current_date+hours_in_shift
            print(shift.since, shift.to)
            shifts_list.append(shift)
        return shifts_list


    def pasteShiftAfter(self, shifts, after):
        # shifts = self.getShiftsForPeriod(after,after)
        new_shifts = []
        if shifts.__len__() > 0:
            delta = after - shifts[0].since
            for shift in shifts:
                ws = WorkingShift(since=shift.since + delta, to=shift.to + delta, scheldue=self)
                new_shifts.append(ws)
            if self.isValidShifts(new_shifts):
                for shift in new_shifts:
                    shift.save()
                return True
            else:
                return False

                # def getShiftsForPeriodWithDurations(self, startDate, endDate):
                #     shifts_list = list(self.getShiftsForPeriod(startDate, endDate))
                #     ret = []
                #     if shifts_list.__len__() > 0:
                #         delta = abs((shifts_list[0].since.replace(tzinfo=None) - startDate).days)
                #         if delta > 0:
                #             ret.append(ShiftDuration(delta*MY_CONST.QUANT_FOR_SCHELDUE, False))
                #     for shifts in shifts_list:
                #         print(shifts.since, shifts.to)
                #         index = shifts_list.index(shifts)
                #         if index == shifts_list.__len__()-1:
                #             delta = abs((shifts.to.replace(tzinfo=None) - endDate).days)
                #             if delta>0:
                #                ret.append(ShiftDuration(delta*MY_CONST.QUANT_FOR_SCHELDUE, False))
                #             # print("last", delta)
                #         else:
                #             delta_min = abs((shifts_list[index+1].since - shifts.to).seconds/60)
                #             print(delta_min)
                #             if delta_min > MY_CONST.QUANT_OF_TIME:
                #                 ret.append(ShiftDuration(delta_min/MY_CONST.MINUTES_IN_DAY*MY_CONST.QUANT_FOR_SCHELDUE, False))

                # return self.getShiftsForPeriod(startDate, endDate)
                # shifts = shifts.order_by('since')
                # print(shifts)
                # if shifts.first().since.year != startDate.year or shifts.first().since.month != startDate.month or shifts.first().since.day != startDate.day:
                #     print(shifts.first().since)
                # return shifts

    def __unicode__(self):
        return self.name


class WorkingShift(models.Model):
    since = models.DateTimeField()
    to = models.DateTimeField()
    image = models.ImageField(upload_to='media/shift', blank=True, max_length=1000, null=True, default='')
    scheldue = models.ForeignKey(Schedule)
    pub_date = models.DateTimeField('date published', default=datetime.datetime.now())

    def deleteWithUserWishes(self):
        userWishes = UserWish.objects.filter(workingShift=self)
        userWishes.delete()
        self.delete()
        #TODO: notification

    def is_night(self):
        if self.since.time()>= self.to.time():
            return True
        if self.since.time()<= datetime.time(hour=6):
            return True
        return False

    def get_workers(self):
        wishes = self.userwish_set.filter(isApproved=True)
        users = []
        for wish in wishes:
            users.append(wish.user)
        return users

    def has_workers(self):
        if self.get_workers().__len__() > 0:
            return True
        else:
            return False

    def shiftsToTheShift(self, shift):
        return self.getShiftsForPeriod(self.since, shift.since)

    def shiftsNumToTheShift(self, shift):
        return self.getShiftsForPeriod(self.since, shift.since).__len__()


    @staticmethod
    def shiftsBetwinTwoShifts(firstShift, secondShift):
        return firstShift.getShiftsForPeriod(firstShift.since, secondShift.since)

    @staticmethod
    def shiftsNumBetwinTwoShifts(firstShift, secondShift):
        return firstShift.getShiftsForPeriod(firstShift.since, secondShift.since).__len__()


    def __unicode__(self):
        return self.since.strftime('%Y.%m %d %H:%M') + self.since.strftime('-%d %H:%M')




class User(AbstractUser):
    workplaces = models.ManyToManyField(Workplace, blank=True, null=True, default='')
    avatar = models.ImageField(upload_to='media/avatar', blank=True, max_length=1000, null=True, default='')
    third_name = models.CharField(max_length=300, blank=True, null=True, default='')
    work_phone = models.CharField(max_length=300, blank=True, null=True, default='')
    mobile_phone = models.CharField(max_length=300, blank=True, null=True, default='')
    # settings = models.OneToOneField(UserSettings, null=True)
    # objects = UserManager()
    #pub_date = models.DateTimeField('date published')

    def __unicode__(self):
        return self.username

    def getFIO(self):
        ret = ''
        if self.last_name:
            ret += self.last_name
        if self.first_name:
            ret += (' '+self.first_name[0]+'.')
        if self.third_name:
            ret += (' '+self.third_name[0]+'.')
        return ret

    @staticmethod
    def getValidUsers(except_users=None):
        all_users = list(User.objects.filter(is_active=True, is_superuser=False))
        if except_users != None:
            for ex_user in except_users:
                for user in all_users:
                    if user.id == ex_user.id:
                        all_users.remove(user)
        return all_users

    # @staticmethod
    # def get_super_user():
    #     users = User.objects.all()
    #     user = User.objects.get()
    #     user.is_superuser
    #     for user in users:
    #         if user.

    def getWorkPlaces(self):
        return self.workplaces.all()

    def addWorkplace(self, workplace):
        self.workplaces.add(workplace)
        self.save()

    def removeWorkplace(self, workplace):
        self.workplaces.remove(workplace)
        self.save()

    def getUserWishes(self, startDate, endDate):
        workplaces = self.getWorkPlaces()
        wishes = []
        for wp in workplaces:
            wish = []
            shifts = wp.getSchedule.getShiftsForPeriod(startDate, endDate)
            DurShift = ShiftDuration.addDuratins(shifts, startDate, endDate)
            for durSh in DurShift:
                if durSh.__len__() > 1:
                    wishesForShift = self.getWishForShift(durSh[1])
                    wish.append([durSh[0], durSh[1], wishesForShift])
                else:
                    wish.append(durSh)
            wishes.append([wp, wish])
        return wishes

    def getUserWishesForWp(self, wp, startDate, endDate):
        wish = []
        shifts = wp.getSchedule.getShiftsForPeriod(startDate, endDate)
        DurShift = ShiftDuration.addDuratins(shifts, startDate, endDate)
        for durSh in DurShift:
            if durSh.__len__() > 1:
                wishesForShift = self.getWishForShift(durSh[1])
                wish.append([durSh[0], durSh[1], wishesForShift])
            else:
                wish.append(durSh)
        return wish

    def getWishForDate(self, date, workPlace):
        userwishes = UserWish.objects.filter(user=self)
        for userWish in userwishes:
            if userWish.getWorkplace() == workPlace and userWish.workingShift.since.day == date.day:
                return userWish
        return "none"

    def getWishForShift(self, shift):
    # wishes = UserWish.objects.filter(user=self, workingShift=shift).order_by('since')
    # for wish in wishes:
    # print(wishes[0].wish.wish)
        return UserWish.objects.filter(user=self, workingShift=shift).order_by('since')

    def getUserWishesforPeriod(self, startDate, endDate):
        workplaces = self.getWorkPlaces()
        wishes = []
        for wp in workplaces:
            shifts = list(wp.getSchedule.getShiftsForPeriodWithDurations(startDate, endDate))
            for shift in shifts:
                user_wish = [shift, self.getWishForShift(shift)]
                # print(user_wish)
                wishes.append([wp, user_wish])
        return wishes

    def getShiftsNumForPeriod(self, startDate, endDate, scheldule):
        first_day = datetime.date(startDate.year, startDate.month, 1)
        last_day = datetime.datetime(endDate.year, endDate.month, calendar.monthrange(endDate.year, endDate.month)[1])
        has_shifts = self.get_working_shifts(first_day, last_day).__len__()
        need_shifts = round(self.usersettings.shiftsInMonth * (endDate - startDate).days/30)
        return need_shifts - has_shifts

    def get_working_shifts(self, startDate, endDate):
        shifts = []
        for wp in self.getWorkPlaces():
            shifts.extend(self.get_working_shifts_for_schedule(startDate, endDate, wp.getSchedule))
        return shifts

    def get_working_shifts_for_schedule(self, startDate, endDate, scheldule):
        shifts = scheldule.getShiftsForPeriod(startDate, endDate)
        working_shifts = []
        for shift in shifts:
            wish = shift.userwish_set.filter(isApproved=True, user=self)
            if wish.__len__()>0:
                working_shifts.append(shift)
        return working_shifts

    def get_last_working_shift(self, shift, days=3, planing_shifts=[]):
        date = shift.since
        last_date = date - datetime.timedelta(days=days)
        working_shifts = self.get_working_shifts(last_date, date)
        working_shifts.extend(planing_shifts)
        last_shift = None
        for shift in working_shifts:
            if last_date < shift.since:
                last_date = shift.since
                last_shift = shift
        return last_shift

    def get_next_working_shift(self, shift, days=3, planing_shifts=[]):
        date = shift.since
        next_date = date + datetime.timedelta(days=days)
        working_shifts = self.get_working_shifts(date, next_date)
        working_shifts.extend(planing_shifts)
        next_shift = None
        for shift in working_shifts:
            if next_date > shift.since:
                next_date = shift.since
                next_shift = shift
        return next_shift

    def could_work_at_shift(self, shift, planing_shifts):
        day = SHIFT_PLANING_SETTINGS.SECONDS_AFTER_DAY_SHIFT
        night = SHIFT_PLANING_SETTINGS.SECONDS_AFTER_NIGHT_SHIFT
        diff = SHIFT_PLANING_SETTINGS.MAX_SECONDS_BETWEN_SHIFTS
        last_shift = self.get_last_working_shift(shift, planing_shifts=planing_shifts)
        next_shift = self.get_next_working_shift(shift)
        # print(self, shift.since)
        # if last_shift!=None:
        #     print('last:', last_shift.since)
        # else:
        #     print('last:', last_shift)
        # if next_shift!=None:
        #     print('next:', next_shift.since)
        # else:
        #     print('next:', next_shift)
        if last_shift == None and next_shift == None:
            return 1
        if self.usersettings.day24Shift:
            if last_shift!= None and abs((last_shift.to - shift.since).total_seconds()) <= diff:
                if next_shift!= None and abs((next_shift.since - shift.to).total_seconds()) <= day:
                    return 0
                else:
                    past_shift = self.get_last_working_shift(last_shift, planing_shifts=planing_shifts)
                    if abs((last_shift.to - past_shift.since).total_seconds()) <= diff:
                        return 0
                    else:
                        return 0.25#TODO: убрать константы
            elif next_shift!= None and abs((next_shift.since - shift.to).total_seconds()) <= diff:
                future_shift = self.get_next_working_shift(next_shift)
                if future_shift != None:
                    return 0
                elif shift.is_night():
                    if last_shift!= None and last_shift.is_night() and abs((last_shift.to - shift.since).total_seconds())<=day:
                        return 0
                    else:
                        return 0.25
                else:
                    if last_shift!= None and abs((last_shift.to - shift.since).total_seconds()) <= day:
                        return 0
                    else:
                        return 0.25
        else:
            if (last_shift!=None and abs((last_shift.to - shift.since).total_seconds()) <= diff) or\
                    (next_shift!=None and abs((next_shift.since - shift.to).total_seconds()) <= diff):
                # print('проверка на сутки')
                if last_shift != None:
                    print('last', last_shift.to, shift.since)
                if next_shift != None:
                    print('next', abs((next_shift.since - shift.to).total_seconds()) )
                return 0  # проверка на сутки
            if shift.is_night():
                if next_shift != None and abs((next_shift.since - shift.to).total_seconds()) <= night:
                    # print('проверка выходных после смены')
                    return 0  # проверка выходных после смены
                else:
                    if last_shift!=None and abs((last_shift.to - shift.since).total_seconds()) <= day:
                        past_shift = self.get_last_working_shift(last_shift, planing_shifts=planing_shifts)
                        if past_shift != None and abs((last_shift.since - past_shift.to).total_seconds()) <= diff:
                            # print('пользователь не может отдохнуть после суочной смены')
                            return 0  # пользователь не может отдохнуть после суочной смены
                        if last_shift.is_night() and abs((last_shift.to - shift.since).total_seconds()) <= night:
                            # print('пользователь не успеет отдохнуть после ночной')
                            return 0  # пользователь не успеет отдохнуть после ночной
                        return 0.5
                    else:
                        return 1
            else:
                if last_shift != None and last_shift.is_night():
                    past_shift = self.get_last_working_shift(last_shift, planing_shifts=planing_shifts)
                    if past_shift == None:
                        return 1
                    else:
                        if abs((last_shift.since - past_shift.to).total_seconds()) <= diff:
                            # print('хз')
                            return 0
                        else:
                            return 1
                    # if abs((last_shift.to - shift.since).total_seconds()) <= night:
                    #     return 0
                    # else:
                    #     return 1
                else:
                    return 1
        return 0

class UserSettings(models.Model):
    #Notifications
    shiftDenied = models.BooleanField(default=True, blank=True)
    shiftActived = models.BooleanField(default=True, blank=True)
    #Auto Assign
    shiftsInMonth = models.IntegerField(blank=True, null=True, default=5)
    nightShift = models.BooleanField(blank=True, default=True, choices=CHOICES_SHIFT_NIGHT)
    day24Shift = models.BooleanField(blank=True, default=True, choices=CHOICES_SHIFT_24DAY)
    user = models.OneToOneField(User, null=True, unique=True)
    # def getUser(self):
    #     self.user
    def __unicode__(self):
        if hasattr(self, 'user'):
            return self.user.username + '_settings'
        else:
            return "no user"


class Notification(models.Model):
    text = models.CharField(max_length=5000)
    page = models.NullBooleanField(choices=CHOICES_NOTIFICATION)
    mail = models.NullBooleanField(choices=CHOICES_NOTIFICATION)
    user = models.ForeignKey(User)
    pub_date = models.DateTimeField('date published', default=datetime.datetime.now())

    @staticmethod
    def UserSetActive(user):
        text = "Поздравляем, вас активировали в системе планирования смен"
        note = Notification(text=text, page=False, mail=False, user=user, pub_date=datetime.datetime.now())
        note.save()

    @staticmethod
    def ShiftDenied(user, shift):
        text = "Вас сняли с дежурства:"+shift.since.strftime("%Y-%m, %d %H:%M") + "-" + shift.to.strftime("%d %H:%M")
        note = Notification(text=text, page=False, mail=False, user=user, pub_date=datetime.datetime.now())
        note.save()

    @staticmethod
    def ShiftActived(user, shift):
        text = "Вас поставили на дежурство:"+shift.since.strftime("%Y-%m, %d %H:%M") + "-" + shift.to.strftime("%d %H:%M")
        note = Notification(text=text, page=False, mail=False, user=user, pub_date=datetime.datetime.now())
        note.save()

    @staticmethod
    def NewUserRegistered(user):
        sUsers = User.objects.filter(is_superuser=True)
        for superuser in sUsers:
            text = "Зарегестрирован новый пользователь" + user.username + " :" + user.getFIO()
            note = Notification(text=text, page=False, mail=False, user=superuser, pub_date=datetime.datetime.now())
            note.save()

    @staticmethod
    def send_mail_notifications():
        notices = Notification.objects.filter(mail=False)
        users = User.objects.filter(is_active=True)
        for user in users:
            user_notes = notices.filter(user=user)
            if user_notes.__len__()>0:
                theme = 'Уведомления: Система Планирования Смен'
                text = 'Здрасвуйте, ' + user.getFIO() + '\n'
                for note in user_notes:
                    text += (note.text + '\n' + note.pub_date.strftime("%Y-%m-%d %H:%M")+'\n')
                    note.mail = True
                    note.save()
                text += ('\n\n Это сообщение  сгенерированно автоматически, на него не нужно отвечать')
                send_mail(theme, text, EMAIL_HOST_USER, [user.email])


class UserWish(models.Model):
    since = models.DateTimeField()
    to = models.DateTimeField()
    wish = models.ForeignKey(WishEnum, blank=True, null=True, default='')
    isApproved = models.BooleanField()
    # schedule = models.ForeignKey(Schedule)
    workingShift = models.ForeignKey(WorkingShift)
    user = models.ForeignKey(User)
    pub_date = models.DateTimeField('date published', default=datetime.datetime.now())

    def getWorkplace(self):
        return self.workingShift.scheldue.workplace

    def __unicode__(self):
        return self.user.username

        # def __int__(self, since, to, wish, schedule, user):
        #     self.since = since
        #     self.to = to
        #     self.wish = wish
        #     self.isApproved = False
        #     self.schedule = schedule
        #     self.user = user





