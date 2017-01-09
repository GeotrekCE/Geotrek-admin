import factory

from geotrek.flatpages import models as flatpages_models


class FlatPageFactory(factory.DjangoModelFactory):
    class Meta:
        model = flatpages_models.FlatPage

    title = factory.Sequence(lambda n: u"Page %s" % n)
    content = factory.Sequence(lambda n: u"<h1>Titre %s</h1>" % n)
    order = factory.Sequence(lambda n: n)

    @classmethod
    def _prepare(cls, create, **kwargs):
        sources = kwargs.pop('sources', None)
        portals = kwargs.pop('portals', None)

        flat = super(FlatPageFactory, cls)._prepare(create, **kwargs)

        if create:
            if sources:
                for source in sources:
                    flat.source.add(source)

            if portals:
                for portal in portals:
                    flat.portal.add(portal)
        return flat
