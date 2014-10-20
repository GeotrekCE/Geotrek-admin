import factory

from geotrek.flatpages import models as flatpages_models


class FlatPageFactory(factory.Factory):
    FACTORY_FOR = flatpages_models.FlatPage

    title = factory.Sequence(lambda n: u"Page %s" % n)
    content = factory.Sequence(lambda n: u"<h1>Titre %s</h1>" % n)
