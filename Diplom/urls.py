from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import Diplom

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'Diplom.views.toindex', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^PlaningSystem/', include('PlaningSystem.urls')),
    url(r'^admin/', include(admin.site.urls)),

)
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)