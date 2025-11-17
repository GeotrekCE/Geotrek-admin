import deepl
from django.core.management import BaseCommand

from geotrek.trekking.models import Trek


class Command(BaseCommand):
    auth_key = ""
    def handle(self, *args, **options):
        for trek in Trek.objects.all():
            translated_description = self.translate_text(trek.description, target_lang="FR")
            trek.description_fr = translated_description
            trek.save()
        auth_key = "f63c02c5-f056-..."  # Replace with your key
        deepl_client = deepl.DeepLClient(auth_key)

        result = deepl_client.translate_text("Hello, world!", target_lang="FR")
        print(result.text)  # "Bonjour, le monde !"