from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$',        'caminae.core.views.home', name='home'),
    url(r'^login/$',  'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout',),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^paperclip/', include('caminae.paperclip.urls')),

    url(r'', include('caminae.mapentity.urls', namespace='mapentity', app_name='mapentity')),
    url(r'', include('caminae.core.urls', namespace='core', app_name='core')),
    url(r'', include('caminae.land.urls', namespace='land', app_name='land')),
    url(r'', include('caminae.infrastructure.urls', namespace='infrastructure', app_name='infrastructure')),
    url(r'', include('caminae.maintenance.urls', namespace='maintenance', app_name='maintenance')),
    url(r'', include('caminae.trekking.urls', namespace='trekking', app_name='trekking')),

    url(r'', include('caminae.common.urls', namespace='common', app_name='common')),
)

urlpatterns += staticfiles_urlpatterns()


# Serve uploaded files from django directly. Assumes settings.MEDIA_URL is set to '/media/'
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
            }),
    )
