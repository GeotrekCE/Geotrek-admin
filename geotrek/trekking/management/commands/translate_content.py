import deepl
from django.conf import settings
from django.core.management import BaseCommand
from modeltranslation.utils import build_localized_fieldname

from geotrek.trekking.models import Trek
from geotrek.trekking.translation import TrekTO


class Command(BaseCommand):
    translatable_fields = [field for field in TrekTO.fields if field != "published"]
    required_languages = [
        lang
        for lang in settings.MODELTRANSLATION_LANGUAGES
        if lang != settings.MODELTRANSLATION_DEFAULT_LANGUAGE
    ]
    def add_arguments(self, parser):
        # limit to specific trek ids comma separated
        parser.add_argument(
            '--treks',
            type=str,
            help='Comma separated list of trek ids to translate. If not provided, all treks will be translated.',
        )
        # limit to languages
        parser.add_argument(
            '--languages',
            type=str,
            help='Comma separated list of language codes to translate to. If not provided, all required languages will be used.',
        )
        # force re-translation
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-translation even if target field is already filled.',
        )
        # check usage of DeepL API key
        parser.add_argument(
            '--check-key',
            action='store_true',
            help='Check DeepL API key usage and exit.',
        )

    def handle(self, *args, **options):
        if not settings.DEEPL_API_KEY:
            self.stderr.write("DEEPL_API_KEY not set in settings or environment variable.")

        deepl_client = deepl.DeepLClient(settings.DEEPL_API_KEY)

        if options.get('check_key'):
            usage = deepl_client.get_usage()
            self.stdout.write(f"DeepL API Usage:")
            self.stdout.write(f"  - {usage.character.count}/{usage.character.limit} characters used this month. ({round(usage.character.count/usage.character.limit*100, 3)}%)")
            self.stdout.write(f"  - Limit reached: {usage.any_limit_reached}")
            return

        treks = Trek.objects.all()
        trek_limit = options.get('treks').split(',') if options.get('treks') else None
        if trek_limit:
            self.stdout.write(f"Limit to treks: {options.get('treks')}")
            treks = treks.filter(id__in=trek_limit)

        languages_opt = options.get('languages')
        if languages_opt:
            languages_list = [l.strip() for l in languages_opt.split(',') if l.strip()]
            allowed = {l.lower() for l in self.required_languages}
            unknown = [l for l in languages_list if l.lower() not in allowed]
            if unknown:
                self.stderr.write(
                    f"Unknown languages requested: {', '.join(unknown)}. Allowed: {', '.join(self.required_languages)}")
                return
            required_languages = languages_list
        else:
            required_languages = self.required_languages

        for trek in treks:  # for each trek
            self.stdout.write(f"Translating trek {trek.id}")
            for field in self.translatable_fields:  # for each translatable field
                self.stdout.write(f"  - field {field}")
                base_field_value = getattr(
                    trek,
                    build_localized_fieldname(
                        field, settings.MODELTRANSLATION_DEFAULT_LANGUAGE
                    ),
                )  # get default value based on default language
                if base_field_value:  # if base value defined
                    for lang in required_languages:
                        self.stdout.write(f"    - {lang}")
                        final_lang = lang.lower() if lang.lower() not in settings.DEEPL_LANGUAGE_FALLBACK else settings.DEEPL_LANGUAGE_FALLBACK[lang.lower()]
                        if final_lang == settings.MODELTRANSLATION_DEFAULT_LANGUAGE:
                            self.stdout.write(
                                f"      - copy {final_lang} as it is the default language"
                            )
                            setattr(
                                trek,
                                build_localized_fieldname(field, lang),
                                base_field_value,
                            )
                        else:
                            target_field_value = getattr(
                                trek, build_localized_fieldname(field, lang)
                            )
                            if not target_field_value or options.get('force'):
                                self.stdout.write(f"request to set {build_localized_fieldname(field, lang)}")
                                try:
                                    result = deepl_client.translate_text(
                                        base_field_value, target_lang=final_lang.upper()
                                    )
                                    setattr(
                                        trek, build_localized_fieldname(field, lang), result
                                    )

                                except deepl.DeepLException as e:
                                    self.stderr.write(
                                        f"Error translating trek {trek.id} to {final_lang}:"
                                    )
                                    self.stderr.write(f"  - {e}")
            trek.save()