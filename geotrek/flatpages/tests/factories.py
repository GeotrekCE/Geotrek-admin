import factory

from geotrek.flatpages import models as flatpages_models


class FlatPageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = flatpages_models.FlatPage

    title = factory.Sequence(lambda n: f"Page {n}")
    content = factory.Sequence(lambda n: f"<h1>Titre {n}</h1>")

    @factory.post_generation
    def sources(obj, create, extracted=None, **kwargs):
        if create and extracted:
            obj.source.set(extracted)

    @factory.post_generation
    def portals(obj, create, extracted=None, **kwargs):
        if create and extracted:
            obj.portals.set(extracted)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class(*args, **kwargs)
        # Initialize tree node
        flatpages_models.FlatPage.add_root(instance=obj)
        obj.save()
        return obj


class MenuItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = flatpages_models.MenuItem

    title = factory.Sequence(lambda n: f"Menu Item {n}")

    @factory.post_generation
    def portals(obj, create, extracted=None, **kwargs):
        if create and extracted:
            obj.portals.set(extracted)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class(*args, **kwargs)
        # Initialize tree node
        flatpages_models.MenuItem.add_root(instance=obj)
        obj.save()
        return obj
