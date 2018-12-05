from django.conf import settings
from django.conf.urls import patterns, include, url, static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

from mapentity.forms import AttachmentForm

handler403 = 'mapentity.views.handler403'
handler404 = 'mapentity.views.handler404'
handler500 = 'mapentity.views.handler500'


urlpatterns = patterns(
    '',
    url(r'^api/v2/', include('geotrek.api.v2.urls', namespace='apiv2', app_name='apiv2')),
    url(r'^$', 'geotrek.core.views.home', name='home'),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': settings.ROOT_URL + '/'}, name='logout',),

    url(r'', include('geotrek.common.urls', namespace='common', app_name='common')),
    url(r'', include('geotrek.core.urls', namespace='core', app_name='core')),
    url(r'', include('geotrek.altimetry.urls', namespace='altimetry', app_name='altimetry')),
    url(r'', include('geotrek.land.urls', namespace='land', app_name='land')),
    url(r'', include('geotrek.zoning.urls', namespace='zoning', app_name='zoning')),
    url(r'', include('geotrek.infrastructure.urls', namespace='infrastructure', app_name='infrastructure')),
    url(r'', include('geotrek.maintenance.urls', namespace='maintenance', app_name='maintenance')),
    url(r'', include('geotrek.trekking.urls', namespace='trekking', app_name='trekking')),
    url(r'', include('geotrek.tourism.urls', namespace='tourism', app_name='tourism')),
    url(r'', include('geotrek.flatpages.urls', namespace='flatpages', app_name='flatpages')),
    url(r'', include('geotrek.feedback.urls', namespace='feedback', app_name='feedback')),



    url(r'', include('mapentity.urls', namespace='mapentity', app_name='mapentity')),
    url(r'^paperclip/add-for/(?P<app_label>[\w\-]+)/(?P<model_name>[\w\-]+)/(?P<pk>\d+)/$',
        'paperclip.views.add_attachment', kwargs={'attachment_form': AttachmentForm}, name="add_attachment"),
    url(r'^paperclip/update/(?P<attachment_pk>\d+)/$', 'paperclip.views.update_attachment',
        kwargs={'attachment_form': AttachmentForm}, name="update_attachment"),
    url(r'^paperclip/', include('paperclip.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG and settings.DEBUG_TOOLBAR:
    try:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
