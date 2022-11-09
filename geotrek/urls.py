from django.conf import settings
from django.urls import include, path, re_path
from django.conf.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.contrib.auth import views as auth_views

from mapentity.forms import AttachmentForm
from mapentity.urls import _MEDIA_URL

from geotrek.common import views as common_views
from geotrek.common.views import add_attachment_accessibility, update_attachment_accessibility, \
    delete_attachment_accessibility, ServeAttachmentAccessibility

from paperclip import views as paperclip_views


urlpatterns = [
    path('', common_views.home, name='home'),
]

if settings.DEBUG or settings.MAPENTITY_CONFIG['SENDFILE_HTTP_HEADER']:
    urlpatterns += [
        re_path(r'^%s/(?P<path>attachments_accessibility/.*)$' % _MEDIA_URL, ServeAttachmentAccessibility.as_view()),
    ]

urlpatterns += [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page=settings.ROOT_URL + '/'), name='logout',),

    path('', include('geotrek.common.urls', namespace='common')),
    path('', include('geotrek.altimetry.urls', namespace='altimetry')),

    path('', include(('mapentity.urls', 'mapentity'), namespace='mapentity')),
    path('paperclip/add-for/<str:app_label>/<str:model_name>/<int:pk>/',
         paperclip_views.add_attachment, kwargs={'attachment_form': AttachmentForm}, name="add_attachment"),
    path('paperclip/update/<int:attachment_pk>/', paperclip_views.update_attachment,
         kwargs={'attachment_form': AttachmentForm}, name="update_attachment"),
    path('trekking/add-accessibility-for/<str:app_label>/<str:model_name>/<int:pk>/',
         add_attachment_accessibility, name="add_attachment_accessibility"),
    path('trekking/update-accessibility/<int:attachment_pk>/', update_attachment_accessibility,
         name="update_attachment_accessibility"),
    path('trekking/delete-accessibility/<int:attachment_pk>/', delete_attachment_accessibility,
         name="delete_attachment_accessibility"),
    path('paperclip/', include('paperclip.urls')),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/clearcache/', include('clearcache.urls')),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
]

if 'geotrek.core' in settings.INSTALLED_APPS:
    urlpatterns.append(path('', include('geotrek.core.urls')))
if 'geotrek.land' in settings.INSTALLED_APPS:
    urlpatterns.append(path('', include('geotrek.land.urls')))
if 'geotrek.zoning' in settings.INSTALLED_APPS:
    urlpatterns.append(path('', include('geotrek.zoning.urls')))
if 'geotrek.infrastructure' in settings.INSTALLED_APPS:
    urlpatterns.append(path('', include('geotrek.infrastructure.urls')))
if 'geotrek.signage' in settings.INSTALLED_APPS:
    urlpatterns.append(path('', include('geotrek.signage.urls')))
if 'geotrek.maintenance' in settings.INSTALLED_APPS:
    urlpatterns.append(path('', include('geotrek.maintenance.urls')))
if 'geotrek.outdoor' in settings.INSTALLED_APPS:
    urlpatterns.append(path('', include('geotrek.outdoor.urls')))
if 'geotrek.trekking' in settings.INSTALLED_APPS:
    urlpatterns.append(path('', include('geotrek.trekking.urls')))
    if 'geotrek.cirkwi' in settings.INSTALLED_APPS:
        urlpatterns.append(path('', include('geotrek.cirkwi.urls')))
if 'geotrek.diving' in settings.INSTALLED_APPS:
    urlpatterns.append(path('', include('geotrek.diving.urls')))
if 'geotrek.tourism' in settings.INSTALLED_APPS:
    urlpatterns.append(path('', include('geotrek.tourism.urls')))
if 'geotrek.flatpages' in settings.INSTALLED_APPS:
    urlpatterns.append(path('', include('geotrek.flatpages.urls')))
if 'geotrek.feedback' in settings.INSTALLED_APPS:
    urlpatterns.append(path('', include('geotrek.feedback.urls')))
if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    urlpatterns.append(path('', include('geotrek.sensitivity.urls')))
if 'geotrek.api' in settings.INSTALLED_APPS:
    urlpatterns.append(path('', include('geotrek.api.v2.urls')))
    if 'geotrek.flatpages' in settings.INSTALLED_APPS and 'geotrek.trekking' in settings.INSTALLED_APPS and 'geotrek.tourism' in settings.INSTALLED_APPS:
        urlpatterns.append(path('', include('geotrek.api.mobile.urls')))

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG or settings.TEST:
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        # Debug toolbar is enabled in dev settings
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
