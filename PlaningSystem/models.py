import datetime
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from PIL import Image

from django.utils.timezone import override


# class MY_CONST(object):
#     MINUTES_IN_DAY = 1440
#     HOURS_IN_DAY = 24
#     MINUTES_IN_HOUR = 60
#     QUANT_FOR_SCHELDUE = HOURS_IN_DAY
#     QUANT_OF_TIME = MINUTES_IN_HOUR

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
    #pub_date = models.DateTimeField('date published')

    def __unicode__(self):
        return self.wish


class Workplace(models.Model):
    name = models.CharField(max_length=300)
    rates = models.ManyToManyField(Rate, blank=True, null=True)
    #pub_date = models.DateTimeField('date published')

    @property
    def getSchedule(self):
        return Schedule.objects.get(workplace=self)

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

    def deleteWithUserWishes(self):
        userWishes = UserWish.objects.filter(workingShift=self)
        userWishes.delete()
        self.delete()

    def __unicode__(self):
        return self.since.strftime('%Y.%m %d %H:%M') + self.since.strftime('-%d %H:%M')


class User(AbstractUser):
    workplaces = models.ManyToManyField(Workplace, blank=True, null=True, default='')
    avatar = models.ImageField(upload_to='media/avatar', blank=True, max_length=1000, null=True, default='')
    third_name = models.CharField(max_length=300, blank=True, null=True, default='')
    work_phone = models.CharField(max_length=300, blank=True, null=True, default='')
    mobile_phone = models.CharField(max_length=300, blank=True, null=True, default='')
    # objects = UserManager()
    #pub_date = models.DateTimeField('date published')

    def __unicode__(self):
        return self.username

    @staticmethod
    def getValidUsers(except_users=None):
        all_users = list(User.objects.filter(is_active=True, is_superuser=False))
        if except_users != None:
            for ex_user in except_users:
                for user in all_users:
                    if user.id == ex_user.id:
                        all_users.remove(user)
        return all_users

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


class UserWish(models.Model):
    since = models.DateTimeField()
    to = models.DateTimeField()
    wish = models.ForeignKey(WishEnum, blank=True, null=True, default='')
    isApproved = models.BooleanField()
    # schedule = models.ForeignKey(Schedule)
    workingShift = models.ForeignKey(WorkingShift)
    user = models.ForeignKey(User)
    #pub_date = models.DateTimeField('date published')

    def getWorkplace(self):
        return self.workingShift.scheldue.workplace

    def __unicode__(self):
        return User.objects.select_related()

        # def __int__(self, since, to, wish, schedule, user):
        #     self.since = since
        #     self.to = to
        #     self.wish = wish
        #     self.isApproved = False
        #     self.schedule = schedule
        #     self.user = user





