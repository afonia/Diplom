from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib.auth.views import login, logout
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from Diplom import settings
from PlaningSystem import views

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Diplom.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^index/$', views.index, name='index'),
    url(r'^user/(?P<user_id>\d+)', views.user, name='user'),
    url(r'^user/save', views.userSave, name='userSave'),
    url(r'^sheldue/(?P<user_id>\d+)', views.userShedule, name='userSheldue'),
    url(r'^sheldue/add', views.userSheduleAdd, name='userSheldueAdd'),
    url(r'^workplace/(?P<workplace_id>\d+)', views.workplace, name='workplace'),
    url(r'^rate/(?P<rate_id>\d+)', views.rate, name='rate'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', views.login, name='login'),
    url(r'^auth/', include('django.contrib.auth.urls', namespace='auth')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/login/$',  login),
    url(r'^accounts/logout/$', logout),
    url(r'^register/$', views.register_user, name='register_user'),
    url(r'^test/$', views.test, name='test'),


# admins urls:
    url(r'^index/admin/$', views.admin, name='admin'),
    #workplaces
    url(r'^workplace/admin/(?P<workplace_id>\d+)', views.workpalceAdmin, name='workplaceAdmin'),
    url(r'^workplace/admin/create', views.workpalceAdminCreate, name='workplaceAdminCreate'),
    url(r'^workplace/change/admin/(?P<workplace_id>\d+)', views.workplaceChangeShiftAdmin, name='workplaceChangeShiftAdmin'),
    url(r'^workplace/users/admin/(?P<workplace_id>\d+)', views.workplaceUsersAdmin, name='workplaceUsersAdmin'),
    url(r'^workplace/rates/admin/(?P<workplace_id>\d+)', views.workplaceRatesAdmin, name='workplaceRatesAdmin'),
    url(r'^scheldue/copy/admin/(?P<scheldue_id>\d+)', views.scheldueCopyShiftsAdmin, name='scheldueCopyShiftsAdmin'),
    #scheldues
    url(r'^scheldue/admin/(?P<scheldue_id>\d+)', views.scheldueAdmin, name='scheldueAdmin'),
    url(r'^scheldue/change/admin/(?P<scheldue_id>\d+)', views.scheldueChangeShiftAdmin, name='scheldueChangeShiftAdmin'),
    url(r'^scheldue/new/admin/(?P<scheldue_id>\d+)', views.scheldueNewShiftAdmin, name='scheldueNewShiftAdmin'),
    url(r'^scheldue/delete/admin/(?P<scheldue_id>\d+)', views.scheldueDeleteShiftAdmin, name='scheldueDeleteShiftAdmin'),
    url(r'^scheldue/copy/admin/(?P<scheldue_id>\d+)', views.scheldueCopyShiftsAdmin, name='scheldueCopyShiftsAdmin'),
    #rates
    url(r'^rate/admin/(?P<rate_id>\d+)', views.rateAdmin, name='rateAdmin'),
    url(r'^rate/change/admin/(?P<rate_id>\d+)', views.rateChangeTCostAdmin, name='rateChangeShiftAdmin'),
    url(r'^rate/new/admin/(?P<rate_id>\d+)', views.rateNewTCostAdmin, name='rateNewShiftAdmin'),
    url(r'^rate/delete/admin/(?P<rate_id>\d+)', views.rateDeleteTCostAdmin, name='rateDeleteShiftAdmin'),
    url(r'^rate/copy/admin/(?P<rate_id>\d+)', views.rateCopyTCostAdmin, name='rateCopyShiftsAdmin'),
    #users
    url(r'^rate/activeUser/admin/', views.activeUserAdmin, name='activeUserAdmin'),


)
