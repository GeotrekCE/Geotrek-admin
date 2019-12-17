from django.conf import settings
from django.conf.urls import include, url, static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.contrib.auth import views as auth_views

from mapentity.forms import AttachmentForm

from geotrek.common import views as common_views

from paperclip import views as paperclip_views


urlpatterns = [
    url(r'^$', common_views.home, name='home'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': settings.ROOT_URL + '/'}, name='logout',),

    url(r'', include('geotrek.common.urls', namespace='common')),
    url(r'', include('geotrek.altimetry.urls', namespace='altimetry')),

    url(r'', include(('mapentity.urls', 'mapentity'), namespace='mapentity')),
    url(r'^paperclip/add-for/(?P<app_label>[\w\-]+)/(?P<model_name>[\w\-]+)/(?P<pk>\d+)/$',
        paperclip_views.add_attachment, kwargs={'attachment_form': AttachmentForm}, name="add_attachment"),
    url(r'^paperclip/update/(?P<attachment_pk>\d+)/$', paperclip_views.update_attachment,
        kwargs={'attachment_form': AttachmentForm}, name="update_attachment"),
    url(r'^paperclip/', include('paperclip.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
]

if 'geotrek.core' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.core.urls', namespace='core')))
if 'geotrek.land' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.land.urls', namespace='land')))
if 'geotrek.zoning' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.zoning.urls', namespace='zoning')))
if 'geotrek.infrastructure' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.infrastructure.urls', namespace='infrastructure')))
if 'geotrek.signage' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.signage.urls', namespace='signage')))
if 'geotrek.maintenance' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.maintenance.urls', namespace='maintenance')))
if 'geotrek.trekking' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.trekking.urls', namespace='trekking')))
if 'geotrek.diving' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.diving.urls', namespace='diving')))
if 'geotrek.tourism' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.tourism.urls', namespace='tourism')))
if 'geotrek.flatpages' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.flatpages.urls', namespace='flatpages')))
if 'geotrek.feedback' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.feedback.urls', namespace='feedback')))
if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'', include('geotrek.sensitivity.urls', namespace='sensitivity')))
if 'geotrek.api' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'^api/v2/', include('geotrek.api.v2.urls', namespace='apiv2')))
    if 'geotrek.flatpages' in settings.INSTALLED_APPS and 'geotrek.trekking' in settings.INSTALLED_APPS and 'geotrek.tourism' in settings.INSTALLED_APPS:
        urlpatterns.append(url(r'^api/mobile/', include('geotrek.api.mobile.urls', namespace='apimobile')))

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG or settings.TEST:
    try:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
