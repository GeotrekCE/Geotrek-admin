import os
from unittest import mock
from shutil import rmtree
from tempfile import mkdtemp
from io import StringIO
from requests import Response
import urllib

from django.test import TestCase
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test.utils import override_settings
from django.template.exceptions import TemplateDoesNotExist

from geotrek.authent.factories import StructureFactory
from geotrek.trekking.models import Trek
from geotrek.common.models import Organism, FileType, Attachment
from geotrek.common.parsers import (
    ExcelParser, AttachmentParserMixin, TourInSoftParser, ValueImportError, DownloadImportError,
    TourismSystemParser, OpenSystemParser,
)


class OrganismParser(ExcelParser):
    model = Organism
    fields = {'organism': 'nOm'}


class OrganismEidParser(ExcelParser):
    model = Organism
    fields = {'organism': 'nOm'}
    eid = 'organism'


class AttachmentParser(AttachmentParserMixin, OrganismEidParser):
    non_fields = {'attachments': 'photo'}


class AttachmentLegendParser(AttachmentParser):

    def filter_attachments(self, src, val):
        (url, legend, author) = val.split(', ')
        return [(url, legend, author)]


class ParserTests(TestCase):
    def test_bad_parser_class(self):
        with self.assertRaisesRegex(CommandError, "Failed to import parser class 'DoesNotExist'"):
            call_command('import', 'geotrek.common.tests.test_parsers.DoesNotExist', '', verbosity=0)

    def test_bad_parser_file(self):
        with self.assertRaisesRegex(CommandError, "Failed to import parser file 'geotrek/common.py'"):
            call_command('import', 'geotrek.common.DoesNotExist', '', verbosity=0)

    def test_no_filename_no_url(self):
        with self.assertRaisesRegex(CommandError, "File path missing"):
            call_command('import', 'geotrek.common.tests.test_parsers.OrganismParser', '', verbosity=0)

    def test_bad_filename(self):
        with self.assertRaisesRegex(CommandError, "File does not exists at: find_me/I_am_not_there.shp"):
            call_command('import', 'geotrek.common.tests.test_parsers.OrganismParser', 'find_me/I_am_not_there.shp', verbosity=0)

    @override_settings(VAR_DIR=os.path.join(os.path.dirname(__file__), 'data'))
    def test_custom_parser(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'organism.xls')
        call_command('import', 'CustomParser', filename, verbosity=0)

    def test_progress(self):
        output = StringIO()
        filename = os.path.join(os.path.dirname(__file__), 'data', 'organism.xls')
        call_command('import', 'geotrek.common.tests.test_parsers.OrganismParser', filename, verbosity=2, stdout=output)
        self.assertIn('(100%)', output.getvalue())

    def test_create(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'organism.xls')
        call_command('import', 'geotrek.common.tests.test_parsers.OrganismParser', filename, verbosity=0)
        self.assertEqual(Organism.objects.count(), 1)
        organism = Organism.objects.get()
        self.assertEqual(organism.organism, "Comité Théodule")

    def test_duplicate_without_eid(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'organism.xls')
        call_command('import', 'geotrek.common.tests.test_parsers.OrganismParser', filename, verbosity=0)
        call_command('import', 'geotrek.common.tests.test_parsers.OrganismParser', filename, verbosity=0)
        self.assertEqual(Organism.objects.count(), 2)

    def test_unmodified_with_eid(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'organism.xls')
        call_command('import', 'geotrek.common.tests.test_parsers.OrganismEidParser', filename, verbosity=0)
        call_command('import', 'geotrek.common.tests.test_parsers.OrganismEidParser', filename, verbosity=0)
        self.assertEqual(Organism.objects.count(), 1)

    def test_updated_with_eid(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'organism.xls')
        filename2 = os.path.join(os.path.dirname(__file__), 'data', 'organism2.xls')
        call_command('import', 'geotrek.common.tests.test_parsers.OrganismEidParser', filename, verbosity=0)
        call_command('import', 'geotrek.common.tests.test_parsers.OrganismEidParser', filename2, verbosity=0)
        self.assertEqual(Organism.objects.count(), 2)
        organisms = Organism.objects.order_by('pk')
        self.assertEqual(organisms[0].organism, "Comité Théodule")
        self.assertEqual(organisms[1].organism, "Comité Hippolyte")

    def test_report_format_text(self):
        parser = OrganismParser()
        self.assertRegex(parser.report(), '0/0 lines imported.')
        self.assertNotRegex(parser.report(), r'<div id=\"collapse-\$celery_id\" class=\"collapse\">')

    def test_report_format_html(self):
        parser = OrganismParser()
        self.assertRegex(parser.report(output_format='html'),
                         r'<div id=\"collapse-\$celery_id\" class=\"collapse\">')

    def test_report_format_bad(self):
        parser = OrganismParser()
        with self.assertRaises(TemplateDoesNotExist):
            parser.report(output_format='toto')


@override_settings(MEDIA_ROOT=mkdtemp('geotrek_test'))
class AttachmentParserTests(TestCase):
    def setUp(self):
        self.filetype = FileType.objects.create(type="Photographie")

    def tearDown(self):
        if os.path.exists(settings.MEDIA_ROOT):
            rmtree(settings.MEDIA_ROOT)

    @mock.patch('requests.get')
    def test_attachment(self, mocked):
        mocked.return_value.status_code = 200
        mocked.return_value.content = ''
        filename = os.path.join(os.path.dirname(__file__), 'data', 'organism.xls')
        call_command('import', 'geotrek.common.tests.test_parsers.AttachmentParser', filename, verbosity=0)
        organism = Organism.objects.get()
        attachment = Attachment.objects.get()
        self.assertEqual(attachment.content_object, organism)
        self.assertEqual(attachment.attachment_file.name, 'paperclip/common_organism/{pk}/titi.png'.format(pk=organism.pk))
        self.assertEqual(attachment.filetype, self.filetype)
        self.assertTrue(os.path.exists(attachment.attachment_file.path), True)

    @mock.patch('requests.get')
    def test_attachment_long_name(self, mocked):
        mocked.return_value.status_code = 200
        mocked.return_value.content = ''
        filename = os.path.join(os.path.dirname(__file__), 'data', 'organism3.xls')
        call_command('import', 'geotrek.common.tests.test_parsers.AttachmentParser', filename, verbosity=0)
        organism = Organism.objects.get()
        attachment = Attachment.objects.get()
        self.assertEqual(attachment.content_object, organism)
        self.assertEqual(attachment.attachment_file.name,
                         'paperclip/common_organism/{pk}/{ti}.png'.format(pk=organism.pk, ti='ti' * 64))
        self.assertEqual(attachment.filetype, self.filetype)
        self.assertTrue(os.path.exists(attachment.attachment_file.path), True)

    @mock.patch('requests.get')
    def test_attachment_long_legend(self, mocked):
        mocked.return_value.status_code = 200
        mocked.return_value.content = ''
        filename = os.path.join(os.path.dirname(__file__), 'data', 'organism4.xls')
        call_command('import', 'geotrek.common.tests.test_parsers.AttachmentLegendParser', filename, verbosity=0)
        organism = Organism.objects.get()
        attachment = Attachment.objects.get()
        # import pdb; pdb.set_trace()
        self.assertEqual(attachment.content_object, organism)
        self.assertEqual(attachment.legend,
                         '{0}'.format(('Legend ' * 18).rstrip()))
        self.assertEqual(attachment.filetype, self.filetype)
        self.assertTrue(os.path.exists(attachment.attachment_file.path), True)

    @mock.patch('requests.get')
    def test_attachment_with_other_filetype_with_structure(self, mocked):
        """
        It will always take the one without structure first
        """
        structure = StructureFactory.create(name="Structure")
        FileType.objects.create(type="Photographie", structure=structure)
        mocked.return_value.status_code = 200
        mocked.return_value.content = ''
        filename = os.path.join(os.path.dirname(__file__), 'data', 'organism.xls')
        call_command('import', 'geotrek.common.tests.test_parsers.AttachmentParser', filename, verbosity=0)
        organism = Organism.objects.get()
        attachment = Attachment.objects.get()
        self.assertEqual(attachment.content_object, organism)
        self.assertEqual(attachment.attachment_file.name, 'paperclip/common_organism/{pk}/titi.png'.format(pk=organism.pk))
        self.assertEqual(attachment.filetype, self.filetype)
        self.assertEqual(attachment.filetype.structure, None)
        self.assertTrue(os.path.exists(attachment.attachment_file.path), True)

    @mock.patch('requests.get')
    def test_attachment_with_no_filetype_photographie(self, mocked):
        self.filetype.delete()
        mocked.return_value.status_code = 200
        mocked.return_value.content = ''
        filename = os.path.join(os.path.dirname(__file__), 'data', 'organism.xls')
        with self.assertRaisesRegex(CommandError, "FileType 'Photographie' does not exists in Geotrek-Admin. Please add it"):
            call_command('import', 'geotrek.common.tests.test_parsers.AttachmentParser', filename, verbosity=0)

    @mock.patch('requests.get')
    @mock.patch('requests.head')
    def test_attachment_not_updated(self, mocked_head, mocked_get):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.content = ''
        mocked_head.return_value.status_code = 200
        mocked_head.return_value.headers = {'content-length': 0}
        filename = os.path.join(os.path.dirname(__file__), 'data', 'organism.xls')
        call_command('import', 'geotrek.common.tests.test_parsers.AttachmentParser', filename, verbosity=0)
        call_command('import', 'geotrek.common.tests.test_parsers.AttachmentParser', filename, verbosity=0)
        self.assertEqual(mocked_get.call_count, 1)
        self.assertEqual(Attachment.objects.count(), 1)

    @override_settings(PARSER_RETRY_SLEEP_TIME=0)
    @mock.patch('requests.get')
    @mock.patch('requests.head')
    def test_attachment_request_fail(self, mocked_head, mocked_get):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.content = ''
        mocked_head.return_value.status_code = 503
        filename = os.path.join(os.path.dirname(__file__), 'data', 'organism.xls')
        call_command('import', 'geotrek.common.tests.test_parsers.AttachmentParser', filename, verbosity=0)
        call_command('import', 'geotrek.common.tests.test_parsers.AttachmentParser', filename, verbosity=0)
        self.assertEqual(mocked_get.call_count, 1)
        self.assertEqual(mocked_head.call_count, 3)
        self.assertEqual(Attachment.objects.count(), 1)

    @mock.patch('requests.get')
    @mock.patch('requests.head')
    def test_attachment_request_except(self, mocked_head, mocked_get):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.content = ''
        mocked_head.side_effect = DownloadImportError()
        filename = os.path.join(os.path.dirname(__file__), 'data', 'organism.xls')
        call_command('import', 'geotrek.common.tests.test_parsers.AttachmentParser', filename, verbosity=0)
        call_command('import', 'geotrek.common.tests.test_parsers.AttachmentParser', filename, verbosity=0)
        self.assertEqual(mocked_get.call_count, 1)
        self.assertEqual(mocked_head.call_count, 1)
        self.assertEqual(Attachment.objects.count(), 1)

    @mock.patch('requests.get')
    @mock.patch('geotrek.common.parsers.urlparse')
    def test_attachment_download_fail(self, mocked_urlparse, mocked_get):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'organism.xls')
        mocked_get.side_effect = DownloadImportError()
        mocked_urlparse.return_value = urllib.parse.urlparse('ftp://test.url.com/organism.xls')

        call_command('import', 'geotrek.common.tests.test_parsers.AttachmentParser', filename, verbosity=0)

        self.assertEqual(mocked_get.call_count, 1)


class TourInSoftParserTests(TestCase):

    def test_attachment(self):
        class TestTourParser(TourInSoftParser):
            separator = '##'
            separator2 = '||'

            def __init__(self):
                self.model = Trek
                super(TestTourParser, self).__init__()

        parser = TestTourParser()
        result = parser.filter_attachments('', 'a||b||c##||||##d||e||f')
        self.assertListEqual(result, [['a', 'b', 'c'], ['d', 'e', 'f']])

    def test_moyen_de_com_split_failure(self):
        class TestTourParser(TourInSoftParser):
            def __init__(self):
                self.model = Trek
                super(TestTourParser, self).__init__()

        parser = TestTourParser()
        with self.assertRaises(ValueImportError):
            parser.filter_email('', 'Téléphone filaire|02 37 37 80 11#Instagram|#chateaudesenonches')
        with self.assertRaises(ValueImportError):
            parser.filter_website('', 'Mél|chateau.senonches@gmail.Com#Instagram|#chateaudesenonches')
        with self.assertRaises(ValueImportError):
            parser.filter_contact('', ('Mél|chateau.senonches@gmail.Com#Instagram|#chateaudesenonches', ''))


class TourismSystemParserTest(TestCase):
    @mock.patch('geotrek.common.parsers.HTTPBasicAuth')
    @mock.patch('requests.get')
    def test_attachment(self, mocked_get, mocked_auth):
        class TestTourismSystemParser(TourismSystemParser):
            def __init__(self):
                self.model = Trek
                self.filename = os.path.join(os.path.dirname(__file__), 'data', 'organism.xls')
                self.filetype = FileType.objects.create(type="Photographie")
                self.login = "test"
                self.password = "test"
                super(TourismSystemParser, self).__init__()

        def side_effect():
            response = Response()
            response.status_code = 200
            response._content = bytes('{\"metadata\": {\"total\": 1}, \"data\": [] }', 'utf-8')
            response.encoding = 'utf-8'
            return response

        mocked_auth.return_value = None
        mocked_get.return_value = side_effect()
        parser = TestTourismSystemParser()
        parser.parse()
        self.assertEqual(mocked_get.call_count, 1)
        self.assertEqual(mocked_auth.call_count, 1)


class OpenSystemParserTest(TestCase):
    @mock.patch('requests.get')
    def test_attachment(self, mocked_get):
        class TestOpenSystemParser(OpenSystemParser):
            def __init__(self):
                self.model = Trek
                self.filename = os.path.join(os.path.dirname(__file__), 'data', 'organism.xls')
                self.filetype = FileType.objects.create(type="Photographie")
                self.login = "test"
                self.password = "test"
                super(OpenSystemParser, self).__init__()

        def side_effect():
            response = Response()
            response.status_code = 200
            response._content = bytes(
                "<?xml version=\"1.0\"?><Data><Resultat><Objets>[]</Objets></Resultat></Data>",
                'utf-8'
            )
            return response

        mocked_get.return_value = side_effect()
        parser = TestOpenSystemParser()
        parser.parse()
        self.assertEqual(mocked_get.call_count, 1)
