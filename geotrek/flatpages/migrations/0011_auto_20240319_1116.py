from django.conf import settings
from django.db import migrations, models
from django.utils import translation
from modeltranslation.translator import translator
from modeltranslation.utils import build_localized_fieldname

from geotrek.flatpages.translation import FlatPageTO
from treebeard.mp_tree import MP_Node
from treebeard.numconv import NumConv


def get_target_type(page):
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
        return "both"
    elif has_link:
        return "link"
    else:
        return "content"


def create_menu_items_from_flatpages(apps, schema_editor):
    MenuItem = apps.get_model('flatpages', 'MenuItem')
    FlatPage = apps.get_model('flatpages', 'FlatPage')

    # This is to avoid fallback on another lang when a translation fields (i.e. `title_en`)
    # has an empty string value. In such a case we want to copy the '' value from `flat_page.title_en` as is.
    FlatPageTO.fallback_undefined = None

    # modeltranslation registration is not run on historical models available during migrations.
    # We register FlatPage for translations now so `title_fr`, `title_es`, etc are defined.
    translator.register(FlatPage, FlatPageTO)

    # MenuItem = type(MenuItem)

    # Those fields are copied from FlatPage to MenuItem
    # keys are FlatPage's fieldnames, values are MenuItem's
    copied_fields = {
        "title": "label",
        "published": "published",
        # "portals": "portals",  # copied but needs to be handled differently
    }

    # Same principle: those fields are moved from FlatPage to MenuItem
    moved_fields = {
        "external_url": "link_url",
        "target": "platform",
    }

    # Those fields are translated so we copy/move all translation values
    translated_fields = [
        "title",
        "published",
        "external_url",
    ]

    # The order by is important as it is the order of creation for MenuItems during this migration
    # which defines their position.
    pages = FlatPage.objects.order_by("order")
    for i, page in enumerate(pages):

        if page.target == "hidden" and get_target_type(page) == "content":
            continue

        # copy fields (including translation fields)
        menu_kwargs = {}

        menu_fields = {}
        menu_fields.update(copied_fields)
        menu_fields.update(moved_fields)

        for src, dst in menu_fields.items():
            if src in translated_fields:
                for lang in settings.MODELTRANSLATION_LANGUAGES:
                    translation.activate(lang)
                    loc_dst = build_localized_fieldname(dst, lang)
                    menu_kwargs[loc_dst] = getattr(page, src)
            else:
                menu_kwargs[dst] = getattr(page, src)

        numconv = NumConv(len(MP_Node.alphabet), MP_Node.alphabet)

        def get_treenode_kwargs(i):

            key = numconv.int2str(i)
            path = '{0}{1}'.format(
                MP_Node.alphabet[0] * (MP_Node.steplen - len(key)),
                key
            )

            return {
                "depth": 1,
                "path": path,
            }

        menu_kwargs.update(get_treenode_kwargs(i))

        # menu_item = MenuItem.add_root(page=page, **menu_kwargs)
        menu_item = MenuItem.objects.create(page=page, **menu_kwargs)

        menu_item.portals.set(page.portals.all())

        # FIXME: is save necessary?
        menu_item.save()


def set_treebeard_path_fields(apps, schema_editor):
    FlatPage = apps.get_model('flatpages', 'FlatPage')
    pages = FlatPage.objects.all()
    for page in pages:
        page.path = str(page.pk)
        page.save()


class Migration(migrations.Migration):

    dependencies = [
        ('flatpages', '0010_auto_20240315_1443'),
    ]

    operations = [
        migrations.RunPython(create_menu_items_from_flatpages),
        migrations.AlterModelOptions(
            name='flatpage',
            options={'permissions': (('read_flatpage', 'Can read FlatPage'),), 'verbose_name': 'Flat page', 'verbose_name_plural': 'Flat pages'},
        ),
        migrations.RenameField(
            model_name='flatpage',
            old_name='portal',
            new_name='portals',
        ),
        migrations.RemoveField(
            model_name='flatpage',
            name='external_url',
        ),
        migrations.RemoveField(
            model_name='flatpage',
            name='order',
        ),
        migrations.RemoveField(
            model_name='flatpage',
            name='target',
        ),
        migrations.AddField(
            model_name='flatpage',
            name='depth',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='flatpage',
            name='numchild',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='flatpage',
            name='path',
            field=models.CharField(default='', max_length=255, unique=True),
            preserve_default=False,
        ),
        migrations.RunPython(set_treebeard_path_fields),
        migrations.AlterField(
            model_name='flatpage',
            name='path',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
