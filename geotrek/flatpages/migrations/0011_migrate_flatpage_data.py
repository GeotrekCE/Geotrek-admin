"""Second script (2/3) of the migration for the MenuItem model

This is a single RunPython operation to create MenuItem instances from the FlatPage instances and copy some fields.

Note that we have to manually register the model classes available during the migration with `modeltranslation`,
otherwise translation fields (from the Python objects side) would be missing.
"""

from django.conf import settings
from django.db import migrations
from django.utils import translation
from modeltranslation.translator import translator, TranslationOptions, AlreadyRegistered
from modeltranslation.utils import build_localized_fieldname

from treebeard.mp_tree import MP_Node
from treebeard.numconv import NumConv


def get_treenode_kwargs(position):
    """Support function to initialize DB fields from django-treebeard package's model MP_Node"""
    numconv = NumConv(len(MP_Node.alphabet), MP_Node.alphabet)
    key = numconv.int2str(position)
    path = '{0}{1}'.format(
        MP_Node.alphabet[0] * (MP_Node.steplen - len(key)),
        key
    )
    return {
        "depth": 1,
        "path": path,
    }


def get_page_type(page):
    """Support function to know what kind of data is on a FlatPage"""
    has_content = False
    for lang in settings.MODELTRANSLATION_LANGUAGES:
        content_fieldname = build_localized_fieldname("content", lang)
        if getattr(page, content_fieldname):
            has_content = True
            break
    has_link = False
    for lang in settings.MODELTRANSLATION_LANGUAGES:
        link_fieldname = build_localized_fieldname("external_url", lang)
        if getattr(page, link_fieldname):
            has_link = True
            break
    if has_content and has_link:
        return "both_content_and_link"
    elif has_link:
        return "link_only"
    else:
        return "content_only"


def create_menu_items_from_flatpages(apps, schema_editor):
    """The data migration from FlatPages to new MenuItems,

    With a lot of comments in the code.
    """

    MenuItem = apps.get_model('flatpages', 'MenuItem')
    FlatPage = apps.get_model('flatpages', 'FlatPage')

    if FlatPage.objects.count() == 0:
        # Not needed when there is no flatpage (running tests, fresh install, ...)
        return

    # Historical models available during migrations do not have custom attributs/methods. Hence they do
    # not expose the translation fields created by the django-modeltranslation package. We have
    # to manually define and register translation fields.
    menu_item_translated_fields = [
        "title",
        "link_url",
    ]
    flatpage_translated_fields = [
        "title",
        "content",
        "external_url",
    ]
    if settings.PUBLISHED_BY_LANG:
        menu_item_translated_fields.append("published")
        flatpage_translated_fields.append("published")

    class MenuItemTO(TranslationOptions):
        fields = menu_item_translated_fields

    class FlatPageTO(TranslationOptions):
        fields = flatpage_translated_fields

    # This is to avoid fallback on another lang when a translation fields (i.e. `title_en`)
    # has an empty string value. In such a case we want to copy the '' value from `flat_page.title_en` as is.
    FlatPageTO.fallback_undefined = None

    # modeltranslation registration is not run on historical models available during migrations.
    # We register FlatPage for translations now so `title_fr`, `title_es`, etc are defined.
    translator.register(FlatPage, FlatPageTO)
    # MenuItem is already translation-registered from the previous migration so we cautiously try
    # (it will be needed to copy values in translation fields)
    try:
        translator.register(MenuItem, MenuItemTO)
    except AlreadyRegistered:
        pass

    # Those fields are copied from FlatPage to MenuItem.
    # Dict keys are FlatPage's fieldnames, dict values are MenuItem's fieldnames.
    copied_fields = {
        "title": "title",
        "published": "published",
        # "portals": "portals",  # copied but needs to be handled differently
    }

    # Same principle: those fields are moved from FlatPage to MenuItem
    moved_fields = {
        "external_url": "link_url",
        "target": "platform",
    }

    # The order-by clause is important as it is the MenuItems' order of creation during this migration
    # which defines their position as tree nodes.
    pages = FlatPage.objects.order_by("order")
    pages_to_delete = []
    for position, page in enumerate(pages):
        page_type = get_page_type(page)
        if page.target == "hidden" and page_type == "content_only":
            # The page is hidden and has no external_url value -> we do not create a MenuItem for it
            continue

        # copy fields (including translation fields)
        menu_kwargs = {}

        menu_fields = {}
        menu_fields.update(copied_fields)
        menu_fields.update(moved_fields)
        for src, dst in menu_fields.items():
            if src in flatpage_translated_fields:
                for lang in settings.MODELTRANSLATION_LANGUAGES:
                    with translation.override(lang):
                        loc_dst = build_localized_fieldname(dst, lang)
                        menu_kwargs[loc_dst] = getattr(page, src)
            else:
                menu_kwargs[dst] = getattr(page, src)

        menu_kwargs.update(get_treenode_kwargs(position))

        # Several cases handled here:
        if page_type == "link_only":
            # FlatPage with only an external_url and no content are "turned into" a MenuItem
            pages_to_delete.append(page)
            menu_kwargs["target_type"] = "link"
        else:
            # Otherwise the new MenuItem targets the FlatPage
            menu_kwargs["page"] = page
            menu_kwargs["target_type"] = "page"

        menu_item = MenuItem.objects.create(**menu_kwargs)

        menu_item.portals.set(page.portal.all())

    for page in pages_to_delete:
        page.delete()

    # Historical models have to be unregistered not to conflict with modeltranslation's sync and update commands which
    # are executed after migrations.
    translator.unregister(MenuItem)
    translator.unregister(FlatPage)


class Migration(migrations.Migration):

    dependencies = [
        ('flatpages', '0010_create_model_MenuItem'),
    ]

    operations = [
        migrations.RunPython(create_menu_items_from_flatpages, reverse_code=migrations.RunPython.noop),
    ]
