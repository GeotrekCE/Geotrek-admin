from django.urls import path
from mapentity.registry import MapEntityOptions

from geotrek.common import views


class PublishableEntityOptions(MapEntityOptions):
    document_public_view = views.DocumentPublic
    document_public_booklet_view = views.DocumentBookletPublic
    markup_public_view = views.MarkupPublic

    def scan_views(self, *args, **kwargs):
        """Adds the URLs of all views provided by ``PublishableMixin`` models."""
        mapentity_views = super().scan_views()
        publishable_views = [
            path(
                f"api/<lang:lang>/{self.modelname}s/<int:pk>/<slug:slug>_booklet.pdf",
                self.document_public_booklet_view.as_view(model=self.model),
                name=f"{self.modelname}_booklet_printable",
            ),
            path(
                f"api/<lang:lang>/{self.modelname}s/<int:pk>/<slug:slug>.pdf",
                self.document_public_view.as_view(model=self.model),
                name=f"{self.modelname}_printable",
            ),
            path(
                f"api/<lang:lang>/{self.modelname}s/<int:pk>/<slug:slug>.html",
                self.markup_public_view.as_view(model=self.model),
                name=f"{self.modelname}_markup_html",
            ),
        ]
        return publishable_views + mapentity_views
