from collections import defaultdict

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db.models import ManyToManyField


class Command(BaseCommand):
    help = "Unset structure in lists of choices and group choices with the same name."

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', help="Manage all models")
        parser.add_argument('--list', action='store_true', help="Show available models to manage")
        parser.add_argument('model', nargs='*', help="List of choices to manage")

    def get_new_fk(self, old_fk, RelatedModel, related_fields):
        if old_fk and old_fk.structure:
            kwargs = {field.name: getattr(old_fk, field.name) for field in related_fields if field.name not in ['date_insert', 'date_update']}
            kwargs['structure'] = None
            return RelatedModel.objects.get(**kwargs)
        return old_fk

    def get_all_items(self):
        self.items = defaultdict(list)
        for app in apps.get_app_configs():
            for Model in app.get_models():
                if Model._meta.proxy:
                    continue
                for field in Model._meta.get_fields():
                    if field.auto_created:
                        continue
                    RelatedModel = field.related_model
                    if not RelatedModel:
                        continue
                    if 'structure' not in [f.name for f in RelatedModel._meta.get_fields()]:
                        continue
                    if not RelatedModel._meta.get_field('structure').null:
                        continue
                    self.items[RelatedModel].append((Model, field.name, isinstance(field, ManyToManyField)))

    def handle_related_model(self, RelatedModel, subitems):
        if self.options['verbosity'] > 0:
            self.stdout.write("Handle related model {}".format(RelatedModel._meta.model_name))

        # Create related objects with structure=None
        related_fields = [field for field in RelatedModel._meta.get_fields() if not field.auto_created]
        for obj in RelatedModel.objects.all():
            kwargs = {field.name: getattr(obj, field.name) for field in related_fields if field.name not in ['date_insert', 'date_update']}
            kwargs['structure'] = None
            new_obj, created = RelatedModel.objects.get_or_create(**kwargs)
            if created and self.options['verbosity'] > 0:
                self.stdout.write("  Create {}".format(new_obj))

        # Update foreign keys
        for Model, fk_name, m2m in subitems:
            if self.options['verbosity'] > 0:
                self.stdout.write("  Handle field {} of model {}".format(fk_name, Model._meta.model_name))
            related_fields = [field for field in RelatedModel._meta.get_fields() if not field.auto_created]
            for obj in Model.objects.all():
                old_fk = getattr(obj, fk_name)
                if m2m:
                    new_fk = [self.get_new_fk(value, RelatedModel, related_fields) for value in old_fk.all()]
                    old_fk.set(new_fk)
                else:
                    new_fk = self.get_new_fk(old_fk, RelatedModel, related_fields)
                    setattr(obj, fk_name, new_fk)
                obj.save()
                if self.options['verbosity'] > 0:
                    self.stdout.write("    Update {}".format(obj))

        # Remove related objects with structure!=None
        related_objs = RelatedModel.objects.exclude(structure=None)
        if related_objs and self.options['verbosity'] > 0:
            self.stdout.write("  Delete {}".format(", ".join([str(obj) for obj in related_objs])))
        related_objs.delete()

    def handle(self, *args, **options):
        self.options = options
        self.get_all_items()

        if options['list']:
            for m in self.items.keys():
                self.stdout.write("{} : {}".format(m._meta.model_name, m._meta.verbose_name))
            return

        if not options['all'] and not options['model']:
            raise CommandError("You should specify model(s) or --all. Use --list to list all possibilities.")

        for RelatedModel, subitems in self.items.items():
            if options['all'] or RelatedModel._meta.model_name in options['model']:
                self.handle_related_model(RelatedModel, subitems)
