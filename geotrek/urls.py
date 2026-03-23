from django.conf import settings
from django.conf.urls import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from mapentity.forms import AttachmentForm
from paperclip import views as paperclip_views

from geotrek.common import views as common_views

urlpatterns = [
    path("", common_views.home, name="home"),
]

urlpatterns += [
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page=settings.ROOT_URL + "/"),
        name="logout",
    ),
    path("", include("geotrek.common.urls", namespace="common")),
    path("", include("geotrek.altimetry.urls", namespace="altimetry")),
    path("", include(("mapentity.urls", "mapentity"), namespace="mapentity")),
    path(
        "paperclip/add-for/<str:app_label>/<str:model_name>/<int:pk>/",
        paperclip_views.add_attachment,
        kwargs={"attachment_form": AttachmentForm},
        name="add_attachment",
    ),
    path(
        "paperclip/update/<int:attachment_pk>/",
        paperclip_views.update_attachment,
        kwargs={"attachment_form": AttachmentForm},
        name="update_attachment",
    ),
    path("paperclip/", include("paperclip.urls")),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/clearcache/", include("clearcache.urls")),
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("maintenance-mode/", include("maintenance_mode.urls")),
    path("mapbox/", include("mapbox_baselayer.urls")),
]

urlpatterns.append(path("", include("geotrek.core.urls")))
urlpatterns.append(path("", include("geotrek.land.urls")))
urlpatterns.append(path("", include("geotrek.zoning.urls")))
urlpatterns.append(path("", include("geotrek.infrastructure.urls")))
urlpatterns.append(path("", include("geotrek.signage.urls")))
urlpatterns.append(path("", include("geotrek.maintenance.urls")))
urlpatterns.append(path("", include("geotrek.outdoor.urls")))
urlpatterns.append(path("", include("geotrek.trekking.urls")))
urlpatterns.append(path("", include("geotrek.cirkwi.urls")))
urlpatterns.append(path("", include("geotrek.diving.urls")))
urlpatterns.append(path("", include("geotrek.tourism.urls")))
urlpatterns.append(path("", include("geotrek.feedback.urls")))
urlpatterns.append(path("", include("geotrek.sensitivity.urls")))
urlpatterns.append(path("flatpages/", include("geotrek.flatpages.urls")))
urlpatterns.append(path("", include("geotrek.api.v2.urls")))
urlpatterns.append(path("", include("geotrek.api.mobile.urls")))

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "geotrek.common.views.handler404"

if settings.DEBUG or settings.TEST:
    if "debug_toolbar" in settings.INSTALLED_APPS:
        # Debug toolbar is enabled in dev settings
        import debug_toolbar

        urlpatterns += [
            path("__debug__/", include(debug_toolbar.urls)),
        ]
