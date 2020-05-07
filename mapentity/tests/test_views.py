import json
import os
import shutil
from unittest import mock
import factory

from django.conf import settings
from django.core.management import call_command
from django.http import Http404
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.exceptions import TemplateDoesNotExist

from mapentity.factories import UserFactory

from mapentity.registry import app_settings
from mapentity.views import serve_attachment, Convert, JSSettings, MapEntityList, map_screenshot


from geotrek.common.models import Attachment
from geotrek.common.models import FileType
from geotrek.trekking.factories import TrekFactory
from geotrek.trekking.views import TrekDocumentPublic, TrekDocument
from geotrek.tourism.filters import TouristicEventFilterSet
from geotrek.tourism.factories import TouristicEventFactory
from geotrek.tourism.models import TouristicEvent
from geotrek.tourism.views import TouristicEventList, TouristicEventDetail
from geotrek.zoning.factories import CityFactory


User = get_user_model()


def get_dummy_uploaded_file(name='file.pdf'):
    return SimpleUploadedFile(name, b'*' * 300, content_type='application/pdf')


class FileTypeFactory(factory.DjangoModelFactory):

    class Meta:
        model = FileType


class AttachmentFactory(factory.DjangoModelFactory):
    """
    Create an attachment. You must provide an 'obj' keywords,
    the object (saved in db) to which the attachment will be bound.
    """

    class Meta:
        model = Attachment

    attachment_file = get_dummy_uploaded_file()
    filetype = factory.SubFactory(FileTypeFactory)

    creator = factory.SubFactory(UserFactory)
    title = factory.Sequence(u"Title {0}".format)
    legend = factory.Sequence(u"Legend {0}".format)


class BaseTest(TestCase):
    def login(self):
        if getattr(self, 'user', None) is None:
            user = User.objects.create_user(self.__class__.__name__ + 'User',
                                            'email@corp.com', 'booh')
            setattr(self, 'user', user)
        self.logout()
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)
        return self.user

    def login_as_superuser(self):
        if getattr(self, 'superuser', None) is None:
            superuser = User.objects.create_superuser(self.__class__.__name__ + 'Superuser',
                                                      'email@corp.com', 'booh')
            setattr(self, 'superuser', superuser)
        self.logout()
        success = self.client.login(username=self.superuser.username, password='booh')
        self.assertTrue(success)
        return self.superuser

    def logout(self):
        self.client.logout()


class ConvertTest(BaseTest):
    def test_view_headers_are_reverted_to_originals(self):
        request = mock.MagicMock(META=dict(HTTP_ACCEPT_LANGUAGE='fr'))
        view = Convert()
        view.request = request
        self.assertEqual(view.request_headers(), {'Accept-Language': 'fr'})

    def test_critical_original_headers_are_filtered(self):
        request = mock.MagicMock(META=dict(HTTP_HOST='originalhost',
                                           HTTP_COOKIE='blah'))
        view = Convert()
        view.request = request
        self.assertEqual(view.request_headers(), {})

    def test_convert_view_is_protected_by_login(self):
        response = self.client.get('/convert/')
        self.assertEqual(response.status_code, 302)

    def test_convert_view_complains_if_no_url_is_provided(self):
        self.login()
        response = self.client.get('/convert/')
        self.assertEqual(response.status_code, 400)

    def test_convert_view_only_supports_get(self):
        self.login()
        response = self.client.head('/convert/')
        self.assertEqual(response.status_code, 405)

    @mock.patch('mapentity.helpers.requests.get')
    def test_convert_view_uses_original_request_headers(self, get_mocked):
        get_mocked.return_value.status_code = 200
        get_mocked.return_value.content = 'x'
        get_mocked.return_value.url = 'x'
        orig = app_settings['CONVERSION_SERVER']
        app_settings['CONVERSION_SERVER'] = 'http://bidule.com:42'
        self.login()
        self.client.get('/convert/?url=http://geotrek.fr',
                        HTTP_ACCEPT_LANGUAGE='it')
        get_mocked.assert_called_with('http://bidule.com:42/?url=http%3A//geotrek.fr&to=application/pdf',
                                      headers={'Accept-Language': 'it'})
        app_settings['CONVERSION_SERVER'] = orig

    @mock.patch('mapentity.helpers.requests.get')
    def test_convert_view_builds_absolute_url_from_relative(self, get_mocked):
        get_mocked.return_value.status_code = 200
        get_mocked.return_value.content = 'x'
        get_mocked.return_value.url = 'x'
        orig = app_settings['CONVERSION_SERVER']
        app_settings['CONVERSION_SERVER'] = 'http://bidule.com:42'
        self.login()
        self.client.get('/convert/?url=/path/1/')
        get_mocked.assert_called_with('http://bidule.com:42/?url=http%3A//testserver/path/1/&to=application/pdf',
                                      headers={})
        app_settings['CONVERSION_SERVER'] = orig


@override_settings(MEDIA_ROOT='/tmp/mapentity-media')
class AttachmentTest(BaseTest):
    def setUp(self):
        app_settings['SENDFILE_HTTP_HEADER'] = 'X-Accel-Redirect'
        self.obj = TouristicEventFactory.create(published=False)
        """
        if os.path.exists(settings.MEDIA_ROOT):
            self.tearDown()
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'paperclip/test_app_dummymodel/{}'.format(self.obj.pk)))
        self.file = os.path.join(settings.MEDIA_ROOT, 'paperclip/test_app_dummymodel/{}/file.pdf'.format(self.obj.pk))
        self.url = '/media/paperclip/test_app_dummymodel/{}/file.pdf'.format(self.obj.pk)
        open(self.file, 'wb').write(b'*' * 300)
        """
        self.attachment = AttachmentFactory.create(content_object=self.obj)
        self.url = "/media/%s" % self.attachment.attachment_file
        call_command('update_geotrek_permissions', verbosity=0)

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)
        app_settings['SENDFILE_HTTP_HEADER'] = None

    def download(self, url):
        return self.client.get(url, REMOTE_ADDR="6.6.6.6")

    def test_access_to_public_attachment(self):
        self.login()
        self.obj.published = True
        self.obj.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_anonymous_access_to_not_published_attachment(self):
        self.login()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_unauthorized_access_to_attachment(self):
        self.login()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_authorized_access_to_attachment(self):
        self.login()
        perm1 = Permission.objects.get(codename='read_attachment')
        self.user.user_permissions.add(perm1)
        perm2 = Permission.objects.get(codename='read_touristicevent')
        self.user.user_permissions.add(perm2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_anonymous_access_to_deleted_object(self):
        self.obj.delete(force=True)
        self.login()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_authorized_access_to_deleted_object(self):
        self.obj.delete(force=True)
        self.login_as_superuser()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_access_to_not_existing_app(self):
        response = self.client.get('/media/paperclip/xxx_dummymodel/{}/file.pdf'.format(self.obj.pk))
        self.assertEqual(response.status_code, 404)

    def test_access_to_not_existing_model(self):
        response = self.client.get('/media/paperclip/test_app_yyy/{}/file.pdf'.format(self.obj.pk))
        self.assertEqual(response.status_code, 404)

    def test_access_to_not_existing_object(self):
        response = self.client.get('/media/paperclip/test_app_dummymodel/99999999/file.pdf')
        self.assertEqual(response.status_code, 404)

    @override_settings(DEBUG=True)
    def test_access_to_not_existing_file(self):
        os.remove(self.attachment.attachment_file.path)
        self.login_as_superuser()
        response = self.download(self.url)
        self.assertEqual(response.status_code, 404)

    @override_settings(DEBUG=True)
    def test_authenticated_user_can_access(self):
        self.login_as_superuser()
        response = self.download(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '*********')

    def test_http_headers_attachment(self):
        app_settings['SENDFILE_HTTP_HEADER'] = 'X-Accel-Redirect'
        request = RequestFactory().get('/fake-path')
        request.user = User.objects.create_superuser('test', 'email@corp.com', 'booh')
        response = serve_attachment(request, str(self.attachment.attachment_file))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')
        self.assertEqual(response['X-Accel-Redirect'], '/media_secure/%s' % self.attachment.attachment_file)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename=%s' % str(self.attachment.attachment_file.name).split('/')[-1])
        app_settings['SENDFILE_HTTP_HEADER'] = None

    def test_http_headers_inline(self):
        app_settings['SERVE_MEDIA_AS_ATTACHMENT'] = False
        request = RequestFactory().get('/fake-path')
        request.user = User.objects.create_superuser('test', 'email@corp.com', 'booh')
        response = serve_attachment(request, str(self.attachment.attachment_file))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertFalse('Content-Disposition' in response)
        app_settings['SERVE_MEDIA_AS_ATTACHMENT'] = True

    def test_serve_attachment_model_nomapentity(self):
        obj = CityFactory.create(code=1)
        attachment = AttachmentFactory.create(content_object=obj)
        request = RequestFactory().get('/fake-path')
        request.user = User.objects.create_superuser('test', 'email@corp.com', 'booh')
        with self.assertRaises(Http404):
            serve_attachment(request, str(attachment.attachment_file))

    def test_serve_attachment_model_no_permission_read(self):
        self.login()
        perm1 = Permission.objects.get(codename='read_attachment')
        self.user.user_permissions.add(perm1)
        request = RequestFactory().get('/fake-path')
        request.user = self.user
        with self.assertRaises(PermissionDenied):
            serve_attachment(request, str(self.attachment.attachment_file))

    def test_map_screenshot_error(self):
        self.login_as_superuser()
        request = RequestFactory().get('/bad-request')
        request.user = self.superuser
        response = map_screenshot(request)
        self.assertEqual(400, response.status_code)

    @mock.patch('mapentity.views.base.capture_image')
    def test_map_screenshot_work(self, mock_capture_image):
        """
        This test do not use normal printcontext it lacks info of the context.
        """
        self.login_as_superuser()
        request = RequestFactory().post('/', data={"printcontext": '{"url":"/path/list/",'
                                                                   '"viewport":{"width":1745,"height":887},'
                                                                   '"selector":"#mainmap"}'})
        request.user = self.superuser
        response = map_screenshot(request)
        self.assertEqual(200, response.status_code)


class TestList(MapEntityList):
    queryset = TouristicEvent.objects.existing()
    filterform = TouristicEventFilterSet
    columns = None


class ViewTestList(BaseTest):
    def test_every_field_column_none(self):
        self.login_as_superuser()
        TouristicEventFactory.create()
        request = RequestFactory().get('/fake-path')
        request.user = self.superuser
        request.session = {}
        view = TestList.as_view()
        response = view(request)
        html = response.render()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Description' in html.content)


class SettingsViewTest(BaseTest):

    def test_js_settings_urls(self):
        view = JSSettings()
        view.request = RequestFactory().get('/fake-path')
        context = view.get_context_data()
        self.assertDictEqual(context['urls'], {
            "layer": "/api/modelname/modelname.geojson",
            "screenshot": "/map_screenshot/",
            "detail": "/modelname/0/",
            "format_list": "/modelname/list/export/",
            "static": "/static/",
            "root": "/"
        })


class ListViewTest(BaseTest):

    def setUp(self):
        self.user = User.objects.create_user('aah', 'email@corp.com', 'booh')

        def user_perms(p):
            return {'tourism.export_touristicevent': False}.get(p, True)

        self.user.has_perm = mock.MagicMock(side_effect=user_perms)

    def test_mapentity_template_is_last_candidate(self):
        listview = TouristicEventList()
        listview.object_list = TouristicEvent.objects.none()
        self.assertEqual(listview.get_template_names()[-1],
                         'mapentity/mapentity_list.html')

    def test_list_should_have_some_perms_in_context(self):
        view = TouristicEventList()
        view.object_list = []
        view.request = RequestFactory().get('/fake-path')
        view.request.user = self.user
        context = view.get_context_data()
        self.assertEqual(context['can_add'], True)
        self.assertEqual(context['can_export'], False)

    def test_list_should_render_some_perms_in_template(self):
        request = RequestFactory().get('/fake-path')
        request.user = self.user
        request.session = {}
        view = TouristicEventList.as_view()
        response = view(request)
        html = response.render()
        self.assertTrue(b'btn-group disabled' in html.content)
        self.assertTrue(b'Add a new touristic event</a>' in html.content)


class MapEntityLayerViewTest(BaseTest):
    def setUp(self):
        TouristicEventFactory.create_batch(30)
        TouristicEventFactory.create(name='toto')

        self.login()
        self.user.is_superuser = True
        self.user.save()
        self.logout()

    def test_geojson_layer_returns_all_by_default(self):
        self.login()
        response = self.client.get(TouristicEvent.get_layer_url())
        self.assertEqual(len(json.loads(response.content.decode())['features']), 31)

    def test_geojson_layer_with_tile_parameter(self):
        self.login()
        response = self.client.get(TouristicEvent.get_layer_url() + '?x=258&y=188&z=9')
        self.assertEqual(len(json.loads(response.content.decode())['features']), 0)

    def test_geojson_layer_can_be_filtered(self):
        self.login()
        response = self.client.get(TouristicEvent.get_layer_url() + '?name=toto')
        self.assertEqual(len(json.loads(response.content.decode())['features']), 1)

    def test_geojson_layer_with_parameters_is_not_cached(self):
        self.login()
        response = self.client.get(TouristicEvent.get_layer_url() + '?name=toto')
        self.assertEqual(len(json.loads(response.content.decode())['features']), 1)
        response = self.client.get(TouristicEvent.get_layer_url())
        self.assertEqual(len(json.loads(response.content.decode())['features']), 31)

    def test_geojson_layer_with_parameters_does_not_use_cache(self):
        self.login()
        response = self.client.get(TouristicEvent.get_layer_url())
        self.assertEqual(len(json.loads(response.content.decode())['features']), 31)
        response = self.client.get(TouristicEvent.get_layer_url() + '?name=toto')
        self.assertEqual(len(json.loads(response.content.decode())['features']), 1)


class DetailViewTest(BaseTest):
    def setUp(self):
        self.login()
        self.user.is_superuser = True
        self.user.save()
        self.logout()
        self.object = TouristicEventFactory.create(name='dumber')

    def test_mapentity_template_is_last_candidate(self):
        detailview = TouristicEventDetail()
        detailview.object = self.object
        self.assertEqual(detailview.get_template_names(),
                         ['tourism/touristicevent_detail.html',
                          'mapentity/mapentity_detail.html'])

    def test_properties_shown_in_extended_template(self):
        self.login()
        response = self.client.get(self.object.get_detail_url())
        self.assertTemplateUsed(response,
                                template_name='tourism/touristicevent_detail.html')
        self.assertContains(response, 'dumber')

    def test_export_buttons_odt(self):
        if app_settings['MAPENTITY_WEASYPRINT']:
            return  # The button is remove when the settings is True initially

        self.login()

        tmp = app_settings['MAPENTITY_WEASYPRINT']
        app_settings['MAPENTITY_WEASYPRINT'] = False

        response = self.client.get(self.object.get_detail_url())

        app_settings['MAPENTITY_WEASYPRINT'] = tmp

        self.assertContains(response, '<a class="btn btn-mini" target="_blank" href="/document/touristicevent-{}.odt">\
<img src="/static/paperclip/fileicons/odt.png"/> ODT</a>'.format(self.object.pk))
        self.assertContains(response, '<a class="btn btn-mini" target="_blank" \
href="/convert/?url=/document/touristicevent-{}.odt&to=doc">\
<img src="/static/paperclip/fileicons/doc.png"/> DOC</a>'.format(self.object.pk))
        self.assertContains(response, '<a class="btn btn-mini" target="_blank" \
href="/convert/?url=/document/touristicevent-{}.odt">\
<img src="/static/paperclip/fileicons/pdf.png"/> PDF</a>'.format(self.object.pk))

    def test_export_buttons_weasyprint(self):
        self.login()

        tmp = app_settings['MAPENTITY_WEASYPRINT']
        app_settings['MAPENTITY_WEASYPRINT'] = True

        response = self.client.get(self.object.get_detail_url())

        app_settings['MAPENTITY_WEASYPRINT'] = tmp

        if app_settings['MAPENTITY_WEASYPRINT']:
            self.assertContains(response, '<a class="btn btn-mini" target="_blank" href="/document/touristicevent-{}.pdf">\
<img src="/static/paperclip/fileicons/pdf.png"/> PDF</a>'.format(self.object.pk))
        else:
            self.assertContains(response, '<a class="btn btn-mini" target="_blank" href="/document/touristicevent-{}.odt">\
<img src="/static/paperclip/fileicons/pdf.png"/> PDF</a>'.format(self.object.pk))
        self.assertNotContains(response, '<a class="btn btn-mini" target="_blank" \
href="/convert/?url=/document/touristicevent-{}.odt&to=doc">\
<img src="/static/paperclip/fileicons/doc.png"/> DOC</a>'.format(self.object.pk))
        self.assertNotContains(response, '<a class="btn btn-mini" target="_blank" \
href="/document/touristicevent-{}.odt"><img src="/static/paperclip/fileicons/odt.png"/> ODT</a>'.format(self.object.pk))


class ViewPermissionsTest(BaseTest):
    def setUp(self):
        self.login()
        self.user.user_permissions.all().delete()  # WTF ?
        self.object = TouristicEventFactory.create()

    def tearDown(self):
        self.logout()

    def test_views_name_depend_on_model(self):
        view = TouristicEventList()
        self.assertEqual(view.get_view_perm(), 'tourism.read_touristicevent')

    def test_unauthorized_list_view_redirects_to_login(self):
        response = self.client.get('/touristicevent/list/')
        self.assertRedirects(response, '/login/')

    def test_unauthorized_detail_view_redirects_to_list(self):
        detail_url = '/touristicevent/%s/' % self.object.pk
        response = self.client.get(detail_url)
        self.assertRedirects(response, '/touristicevent/list/',
                             target_status_code=302)  # --> login

    def test_unauthorized_add_view_redirects_to_list(self):
        add_url = '/touristicevent/add/'
        response = self.client.get(add_url)
        self.assertRedirects(response, '/touristicevent/list/',
                             target_status_code=302)  # --> login

    def test_unauthorized_update_view_redirects_to_detail(self):
        edit_url = '/touristicevent/edit/%s/' % self.object.pk
        response = self.client.get(edit_url)
        self.assertRedirects(response, '/touristicevent/%s/' % (self.object.pk),
                             target_status_code=302)  # --> login

    def test_unauthorized_delete_view_redirects_to_detail(self):
        delete_url = '/touristicevent/delete/%s/' % self.object.pk
        response = self.client.get(delete_url)
        self.assertRedirects(response, '/touristicevent/%s/' % (self.object.pk),
                             target_status_code=302)  # --> login


class LogViewTest(BaseTest):
    def test_logentry_view(self):
        self.login_as_superuser()
        response = self.client.get('/logentry/list/')
        self.assertContains(response, "<th>action flag</th>")

    def test_logentry_view_not_logged(self):
        response = self.client.get('/logentry/list/')
        self.assertRedirects(response, "/login/")

    def test_logentry_view_not_superuser(self):
        self.login()
        response = self.client.get('/logentry/list/')
        self.assertRedirects(response, "/login/")


class TemplateTest(BaseTest):
    @mock.patch('mapentity.views.generic.smart_get_template', return_value=None)
    def test_no_template_pdf(self, mock_get_template):
        self.login_as_superuser()
        request = RequestFactory().get('/fake-path')
        request.user = self.superuser
        request.session = {}
        trek = TrekFactory.create()
        view = TrekDocumentPublic.as_view()
        with self.assertRaises(TemplateDoesNotExist):
            view(request, pk=trek.pk, slug=trek.slug)

    @mock.patch('mapentity.views.generic.smart_get_template', return_value=None)
    def test_no_template_odt(self, mock_get_template):
        self.login_as_superuser()
        request = RequestFactory().get('/fake-path')
        request.user = self.superuser
        request.session = {}
        trek = TrekFactory.create()
        view = TrekDocument.as_view()
        with self.assertRaises(TemplateDoesNotExist):
            view(request, pk=trek.pk, slug=trek.slug)
