from django.conf import settings
from django.conf.urls import include, url, static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.contrib.auth import views as auth_views

from mapentity.forms import AttachmentForm

from geotrek.common import views as common_views

from paperclip import views as paperclip_views

handler403 = 'mapentity.views.handler403'
handler404 = 'mapentity.views.handler404'


urlpatterns = [
    url(r'^$', common_views.home, name='home'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout',),

    url(r'', include('geotrek.common.urls', namespace='common', app_name='common')),
    url(r'', include('geotrek.altimetry.urls', namespace='altimetry', app_name='altimetry')),

    url(r'', include('mapentity.urls', namespace='mapentity', app_name='mapentity')),
    url(r'^paperclip/add-for/(?P<app_label>[\w\-]+)/(?P<model_name>[\w\-]+)/(?P<pk>\d+)/$',
        paperclip_views.add_attachment, kwargs={'attachment_form': AttachmentForm}, name="add_attachment"),
    url(r'^paperclip/update/(?P<attachment_pk>\d+)/$', paperclip_views.update_attachment,
        kwargs={'attachment_form': AttachmentForm}, name="update_attachment"),
    url(r'^paperclip/', include('paperclip.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
]

if 'geotrek.core' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.core.urls', namespace='core', app_name='core')))
if 'geotrek.land' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.land.urls', namespace='land', app_name='land')))
if 'geotrek.zoning' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.zoning.urls', namespace='zoning', app_name='zoning')))
if 'geotrek.infrastructure' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.infrastructure.urls', namespace='infrastructure',
                                        app_name='infrastructure')))
if 'geotrek.maintenance' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.maintenance.urls', namespace='maintenance', app_name='maintenance')))
if 'geotrek.trekking' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.trekking.urls', namespace='trekking', app_name='trekking')))
if 'geotrek.tourism' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.tourism.urls', namespace='tourism', app_name='tourism')))
if 'geotrek.flatpages' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.flatpages.urls', namespace='flatpages', app_name='flatpages')))
if 'geotrek.feedback' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.feedback.urls', namespace='feedback', app_name='feedback')))
if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.sensitivity.urls', namespace='sensitivity', app_name='sensitivity')))
if 'geotrek.api' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'^api/v2/', include('geotrek.api.v2.urls', namespace='apiv2', app_name='apiv2')))

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
