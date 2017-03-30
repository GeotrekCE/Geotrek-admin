# -*- encoding: utf-8 -*-

import os
import re
import requests
from requests.auth import HTTPBasicAuth
import xlrd
import xml.etree.ElementTree as ET
import urllib2

from ftplib import FTP
from os.path import dirname
from urlparse import urlparse

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.gdal import DataSource
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text

from modeltranslation.fields import TranslationField
from modeltranslation.translator import translator, NotRegistered
from paperclip.models import attachment_upload

from geotrek.authent.models import default_structure
from geotrek.common.models import FileType, Attachment


class ImportError(Exception):
    pass


class GlobalImportError(ImportError):
    pass


class RowImportError(ImportError):
    pass


class ValueImportError(ImportError):
    pass


class Parser(object):
    label = None
    filename = None
    url = None
    simplify_tolerance = 0  # meters
    update_only = False
    delete = False
    duplicate_eid_allowed = False
    warn_on_missing_fields = False
    warn_on_missing_objects = False
    separator = '+'
    eid = None
    fields = None
    m2m_fields = {}
    constant_fields = {}
    m2m_constant_fields = {}
    non_fields = {}
    natural_keys = {}
    field_options = {}

    def __init__(self, progress_cb=None):
        self.warnings = {}
        self.line = 0
        self.nb_success = 0
        self.nb_created = 0
        self.nb_updated = 0
        self.nb_unmodified = 0
        self.progress_cb = progress_cb

        try:
            mto = translator.get_options_for_model(self.model)
        except NotRegistered:
            self.translated_fields = []
        else:
            self.translated_fields = mto.fields.keys()

        if self.fields is None:
            self.fields = {
                f.name: force_text(f.verbose_name)
                for f in self.model._meta.fields
                if not isinstance(f, TranslationField)
            }
            self.m2m_fields = {
                f.name: force_text(f.verbose_name)
                for f in self.model._meta.many_to_many
            }

    def normalize_field_name(self, name):
        return name.upper()

    def normalize_src(self, src):
        if hasattr(src, '__iter__'):
            return [self.normalize_field_name(subsrc) for subsrc in src]
        else:
            return self.normalize_field_name(src)

    def add_warning(self, msg):
        key = _(u"Line {line}".format(line=self.line))
        warnings = self.warnings.setdefault(key, [])
        warnings.append(msg)

    def get_part(self, dst, src, val):
        if not src:
            return val
        if val is None:
            return None
        if '.' in src:
            part, left = src.split('.', 1)
        else:
            part, left = src, ''
        if part.isdigit():
            return self.get_part(dst, left, val[int(part)])
        elif part == '*':
            return [self.get_part(dst, left, subval) for subval in val]
        else:
            return self.get_part(dst, left, val[part])

    def get_val(self, row, dst, src):
        if hasattr(src, '__iter__'):
            val = []
            for subsrc in src:
                try:
                    val.append(self.get_val(row, dst, subsrc))
                except ValueImportError as warning:
                    if self.warn_on_missing_fields:
                        self.add_warning(unicode(warning))
                    val.append(None)
            return val
        else:
            try:
                return self.get_part(dst, src, row)
            except (KeyError, IndexError):
                required = u"required " if self.field_options.get(dst, {}).get('required', False) else ""
                raise ValueImportError(_(u"Missing {required}field '{src}'").format(required=required, src=src))

    def apply_filter(self, dst, src, val):
        field = self.model._meta.get_field_by_name(dst)[0]
        if (isinstance(field, models.ForeignKey) or isinstance(field, models.ManyToManyField)):
            if dst not in self.natural_keys:
                raise ValueImportError(_(u"Destination field '{dst}' not in natural keys configuration").format(dst=dst))
            to = field.rel.to
            natural_key = self.natural_keys[dst]
            kwargs = self.field_options.get(dst, {})
            if isinstance(field, models.ForeignKey):
                val = self.filter_fk(src, val, to, natural_key, **kwargs)
            else:
                val = self.filter_m2m(src, val, to, natural_key, **kwargs)
        return val

    def parse_non_field(self, dst, src, val):
        """Returns True if modified"""
        if hasattr(self, 'save_{0}'.format(dst)):
            return getattr(self, 'save_{0}'.format(dst))(src, val)

    def set_value(self, dst, src, val):
        field = self.model._meta.get_field_by_name(dst)[0]
        if val is None and not field.null:
            if field.blank and (isinstance(field, models.CharField) or isinstance(field, models.TextField)):
                val = u""
            else:
                raise RowImportError(_(u"Null value not allowed for field '{src}'".format(src=src)))
        if val == u"" and not field.blank:
            raise RowImportError(_(u"Blank value not allowed for field '{src}'".format(src=src)))
        setattr(self.obj, dst, val)

    def parse_real_field(self, dst, src, val):
        """Returns True if modified"""
        if hasattr(self, 'filter_{0}'.format(dst)):
            val = getattr(self, 'filter_{0}'.format(dst))(src, val)
        else:
            val = self.apply_filter(dst, src, val)
        if hasattr(self.obj, dst):
            if dst in self.m2m_fields or dst in self.m2m_constant_fields:
                old = set(getattr(self.obj, dst).all())
                val = set(val)
            else:
                old = getattr(self.obj, dst)
            if isinstance(old, float) and isinstance(val, float):
                old = round(old, 10)
                val = round(val, 10)
            if old != val:
                self.set_value(dst, src, val)
                return True
            else:
                return False
        else:
            self.set_value(dst, src, val)
            return True

    def parse_field(self, row, dst, src, updated, non_field):
        if dst in self.constant_fields:
            val = self.constant_fields[dst]
        elif dst in self.m2m_constant_fields:
            val = self.m2m_constant_fields[dst]
        else:
            src = self.normalize_src(src)
            val = self.get_val(row, dst, src)
        if non_field:
            modified = self.parse_non_field(dst, src, val)
        else:
            modified = self.parse_real_field(dst, src, val)
        if modified:
            updated.append(dst)
            if dst in self.translated_fields:
                lang = translation.get_language()
                updated.append('{field}_{lang}'.format(field=dst, lang=lang))

    def parse_fields(self, row, fields, non_field=False):
        updated = []
        for dst, src in fields.items():
            try:
                self.parse_field(row, dst, src, updated, non_field)
            except ValueImportError as warning:
                if self.field_options.get(dst, {}).get('required', False):
                    raise RowImportError(warning)
                if self.warn_on_missing_fields:
                    self.add_warning(unicode(warning))
                continue
        return updated

    def parse_obj(self, row, operation):
        try:
            update_fields = self.parse_fields(row, self.fields)
            update_fields += self.parse_fields(row, self.constant_fields)
        except RowImportError as warnings:
            self.add_warning(unicode(warnings))
            return
        if operation == u"created":
            self.obj.save()
        else:
            self.obj.save(update_fields=update_fields)
        update_fields += self.parse_fields(row, self.m2m_fields)
        update_fields += self.parse_fields(row, self.m2m_constant_fields)
        update_fields += self.parse_fields(row, self.non_fields, non_field=True)
        if operation == u"created":
            self.nb_created += 1
        elif update_fields:
            self.nb_updated += 1
        else:
            self.nb_unmodified += 1

    def get_eid_kwargs(self, row):
        try:
            eid_src = self.fields[self.eid]
        except KeyError:
            raise GlobalImportError(_(u"Eid field '{eid_dst}' missing in parser configuration").format(eid_dst=self.eid))
        eid_src = self.normalize_field_name(eid_src)
        try:
            eid_val = self.get_val(row, self.eid, eid_src)
        except KeyError:
            raise GlobalImportError(_(u"Missing id field '{eid_src}'").format(eid_src=eid_src))
        if hasattr(self, 'filter_{0}'.format(self.eid)):
            eid_val = getattr(self, 'filter_{0}'.format(self.eid))(eid_src, eid_val)
        self.eid_src = eid_src
        self.eid_val = eid_val
        return {self.eid: eid_val}

    def parse_row(self, row):
        self.eid_val = None
        self.line += 1
        if self.eid is None:
            eid_kwargs = {}
            objects = self.model.objects.none()
        else:
            try:
                eid_kwargs = self.get_eid_kwargs(row)
            except RowImportError as warnings:
                self.add_warning(unicode(warnings))
                return
            objects = self.model.objects.filter(**eid_kwargs)
        if len(objects) == 0 and self.update_only:
            if self.warn_on_missing_objects:
                self.add_warning(_(u"Bad value '{eid_val}' for field '{eid_src}'. No object with this identifier").format(eid_val=self.eid_val, eid_src=self.eid_src))
            return
        elif len(objects) == 0:
            objects = [self.model(**eid_kwargs)]
            operation = u"created"
        elif len(objects) >= 2 and not self.duplicate_eid_allowed:
            self.add_warning(_(u"Bad value '{eid_val}' for field '{eid_src}'. Multiple objects with this identifier").format(eid_val=self.eid_val, eid_src=self.eid_src))
            return
        else:
            operation = u"updated"
        for self.obj in objects:
            self.parse_obj(row, operation)
            self.to_delete.discard(self.obj.pk)
        self.nb_success += 1  # FIXME
        if self.progress_cb:
            self.progress_cb(float(self.line) / self.nb, self.line, self.eid_val)

    def report(self, output_format='txt'):
        context = {
            'nb_success': self.nb_success,
            'nb_lines': self.line,
            'nb_created': self.nb_created,
            'nb_updated': self.nb_updated,
            'nb_deleted': len(self.to_delete) if self.delete else None,
            'nb_unmodified': self.nb_unmodified,
            'warnings': self.warnings,
        }
        return render_to_string('common/parser_report.{output_format}'.format(output_format=output_format), context)

    def get_mapping(self, src, val, mapping, partial):
        if partial:
            found = False
            for i, j in mapping.iteritems():
                if i in val:
                    val = j
                    found = True
                    break
            if not found:
                self.add_warning(_(u"Bad value '{val}' for field {src}. Should contain {values}").format(val=val, src=src, separator=self.separator, values=', '.join(mapping.keys())))
                return None
        else:
            if mapping is not None:
                if val not in mapping.keys():
                    self.add_warning(_(u"Bad value '{val}' for field {src}. Should be {values}").format(val=val, src=src, separator=self.separator, values=', '.join(mapping.keys())))
                    return None
                val = mapping[val]
        return val

    def filter_fk(self, src, val, model, field, mapping=None, partial=False, create=False):
        val = self.get_mapping(src, val, mapping, partial)
        if val is None:
            return None
        if create:
            val, created = model.objects.get_or_create(**{field: val})
            if created:
                self.add_warning(_(u"{model} '{val}' did not exist in Geotrek-Admin and was automatically created").format(model=model._meta.verbose_name.title(), val=val))
            return val
        try:
            return model.objects.get(**{field: val})
        except model.DoesNotExist:
            self.add_warning(_(u"{model} '{val}' does not exists in Geotrek-Admin. Please add it").format(model=model._meta.verbose_name.title(), val=val))
            return None

    def filter_m2m(self, src, val, model, field, mapping=None, partial=False, create=False):
        if not val:
            return []
        if self.separator and not isinstance(val, list):
            val = val.split(self.separator)
        dst = []
        for subval in val:
            subval = subval.strip()
            subval = self.get_mapping(src, subval, mapping, partial)
            if subval is None:
                continue
            if create:
                subval, created = model.objects.get_or_create(**{field: subval})
                if created:
                    self.add_warning(_(u"{model} '{val}' did not exist in Geotrek-Admin and was automatically created").format(model=model._meta.verbose_name.title(), val=subval))
                dst.append(subval)
                continue
            try:
                dst.append(model.objects.get(**{field: subval}))
            except model.DoesNotExist:
                self.add_warning(_(u"{model} '{val}' does not exists in Geotrek-Admin. Please add it").format(model=model._meta.verbose_name.title(), val=subval))
                continue
        return dst

    def start(self):
        # FIXME: use mapping if it exists
        kwargs = {}
        for dst, val in self.constant_fields.iteritems():
            field = self.model._meta.get_field_by_name(dst)[0]
            if isinstance(field, models.ForeignKey):
                natural_key = self.natural_keys[dst]
                try:
                    kwargs[dst] = field.rel.to.objects.get(**{natural_key: val})
                except field.rel.to.DoesNotExist:
                    raise GlobalImportError(_(u"{model} '{val}' does not exists in Geotrek-Admin. Please add it").format(model=field.rel.to._meta.verbose_name.title(), val=val))
            else:
                kwargs[dst] = val
        for dst, val in self.m2m_constant_fields.iteritems():
            assert not self.separator or self.separator not in val
            field = self.model._meta.get_field_by_name(dst)[0]
            natural_key = self.natural_keys[dst]
            try:
                kwargs[dst] = field.rel.to.objects.get(**{natural_key: subval for subval in val})
            except field.rel.to.DoesNotExist:
                raise GlobalImportError(_(u"{model} '{val}' does not exists in Geotrek-Admin. Please add it").format(model=field.rel.to._meta.verbose_name.title(), val=val))
        self.to_delete = set(self.model.objects.filter(**kwargs).values_list('pk', flat=True))

    def end(self):
        if self.delete:
            self.model.objects.filter(pk__in=self.to_delete).delete()

    def parse(self, filename=None, limit=None):
        if filename:
            self.filename = filename
        if not self.url and not self.filename:
            raise GlobalImportError(_(u"Filename is required"))
        if self.filename and not os.path.exists(self.filename):
            raise GlobalImportError(_(u"File does not exists at: {filename}").format(filename=self.filename))
        self.start()
        for i, row in enumerate(self.next_row()):
            if limit and i >= limit:
                break
            try:
                self.parse_row(row)
            except Exception as e:
                if settings.DEBUG:
                    raise
                self.add_warning(unicode(e))
        self.end()


class ShapeParser(Parser):
    encoding = 'utf-8'

    def next_row(self):
        datasource = DataSource(self.filename, encoding=self.encoding)
        layer = datasource[0]
        self.nb = len(layer)
        for i, feature in enumerate(layer):
            row = {self.normalize_field_name(field.name): field.value for field in feature}
            try:
                ogrgeom = feature.geom
            except:
                print _(u"Invalid geometry pointer"), i
                geom = None
            else:
                ogrgeom.coord_dim = 2  # Flatten to 2D
                geom = ogrgeom.geos
            if self.simplify_tolerance and geom is not None:
                geom = geom.simplify(self.simplify_tolerance)
            row[self.normalize_field_name('geom')] = geom
            yield row

    def normalize_field_name(self, name):
        """Shapefile field names length is 10 char max"""
        name = super(ShapeParser, self).normalize_field_name(name)
        return name[:10]


class ExcelParser(Parser):
    def next_row(self):
        workbook = xlrd.open_workbook(self.filename)
        sheet = workbook.sheet_by_index(0)
        header = [self.normalize_field_name(cell.value) for cell in sheet.row(0)]
        self.nb = sheet.nrows - 1
        for i in range(1, sheet.nrows):
            values = [cell.value for cell in sheet.row(i)]
            row = dict(zip(header, values))
            yield row


class AtomParser(Parser):
    ns = {
        'Atom': 'http://www.w3.org/2005/Atom',
        'georss': 'http://www.georss.org/georss',
    }

    def flatten_fields(self, fields):
        return reduce(lambda x, y: x + (list(y) if hasattr(y, '__iter__') else [y]), fields.values(), [])

    def next_row(self):
        srcs = self.flatten_fields(self.fields)
        srcs += self.flatten_fields(self.m2m_fields)
        srcs += self.flatten_fields(self.non_fields)
        tree = ET.parse(self.filename)
        entries = tree.getroot().findall('Atom:entry', self.ns)
        self.nb = len(entries)
        for entry in entries:
            row = {self.normalize_field_name(src): entry.find(src, self.ns).text for src in srcs}
            yield row


class AttachmentParserMixin(object):
    download_attachments = True
    base_url = ''
    delete_attachments = False
    filetype_name = u"Photographie"
    non_fields = {
        'attachments': _(u"Attachments"),
    }

    def start(self):
        super(AttachmentParserMixin, self).start()
        if settings.PAPERCLIP_ENABLE_LINK is False and self.download_attachments is False:
            raise Exception(u'You need to enable PAPERCLIP_ENABLE_LINK to use this function')
        try:
            self.filetype = FileType.objects.get(type=self.filetype_name, structure=default_structure())
        except FileType.DoesNotExist:
            raise GlobalImportError(_(u"FileType '{name}' does not exists in Geotrek-Admin. Please add it").format(name=self.filetype_name))
        self.creator, created = get_user_model().objects.get_or_create(username='import', defaults={'is_active': False})

    def filter_attachments(self, src, val):
        if not val:
            return []
        return [(subval.strip(), '', '') for subval in val.split(self.separator) if subval.strip()]

    def has_size_changed(self, url, attachment):
        try:
            parsed_url = urlparse(url)
            if parsed_url.scheme == 'ftp':
                directory = dirname(parsed_url.path)

                ftp = FTP(parsed_url.hostname)
                ftp.login(user=parsed_url.username, passwd=parsed_url.password)
                ftp.cwd(directory)
                size = ftp.size(parsed_url.path.split('/')[-1:][0])
                return size != attachment.attachment_file.size

            if parsed_url.scheme == 'http' or parsed_url.scheme == 'https':
                http = urllib2.urlopen(url)
                size = http.headers.getheader('content-length')
                return int(size) != attachment.attachment_file.size
        except:
            return False

        return True

    def download_attachment(self, url):
        parsed_url = urlparse(url)
        if parsed_url.scheme == 'ftp':
            try:
                response = urllib2.urlopen(url)
            except:
                self.add_warning(_(u"Failed to download '{url}'").format(url=url))
                return None
            return response.read()
        else:
            if self.download_attachments:
                try:
                    response = requests.get(url)
                except requests.exceptions.RequestException as e:
                    raise ValueImportError('Failed to load attachment: {exc}'.format(exc=e))
                if response.status_code != requests.codes.ok:
                    self.add_warning(_(u"Failed to download '{url}'").format(url=url))
                    return None
                return response.content
            return None

    def save_attachments(self, src, val):
        updated = False
        attachments_to_delete = list(Attachment.objects.attachments_for_object(self.obj))
        for url, legend, author in self.filter_attachments(src, val):
            url = self.base_url + url
            legend = legend or u""
            author = author or u""
            name = os.path.basename(url)
            found = False
            for attachment in attachments_to_delete:
                upload_name, ext = os.path.splitext(attachment_upload(attachment, name))
                existing_name = attachment.attachment_file.name
                if re.search(ur"^{name}(_\d+)?{ext}$".format(name=upload_name, ext=ext), existing_name) and not self.has_size_changed(url, attachment):
                    found = True
                    attachments_to_delete.remove(attachment)
                    if author != attachment.author or legend != attachment.legend:
                        attachment.author = author
                        attachment.legend = legend
                        attachment.save()
                        updated = True
                    break
            if found:
                continue

            parsed_url = urlparse(url)

            attachment = Attachment()
            attachment.content_object = self.obj
            attachment.filetype = self.filetype
            attachment.creator = self.creator
            attachment.author = author
            attachment.legend = legend

            if (parsed_url.scheme in ('http', 'https') and self.download_attachments) or parsed_url.scheme == 'ftp':
                content = self.download_attachment(url)
                if content is None:
                    continue
                f = ContentFile(content)
                attachment.attachment_file.save(name, f, save=False)
            else:
                attachment.attachment_link = url
            attachment.save()
            updated = True

        if self.delete_attachments:
            for att in attachments_to_delete:
                att.delete()
        return updated


class TourInSoftParser(AttachmentParserMixin, Parser):
    @property
    def items(self):
        return self.root['d']['results']

    def next_row(self):
        skip = 0
        while True:
            params = {
                '$format': 'json',
                '$inlinecount': 'allpages',
                '$top': 1000,
                '$skip': skip,
            }
            response = requests.get(self.url, params=params)
            if response.status_code != 200:
                raise GlobalImportError(_(u"Failed to download {url}. HTTP status code {status_code}").format(url=self.url, status_code=response.status_code))
            self.root = response.json()
            self.nb = int(self.root['d']['__count'])
            for row in self.items:
                yield {self.normalize_field_name(src): val for src, val in row.iteritems()}
            skip += 1000
            if skip >= self.nb:
                return

    def filter_attachments(self, src, val):
        if not val:
            return []
        return [subval.split('||') for subval in val.split('##') if subval.split('||')[0]]


class TourismSystemParser(AttachmentParserMixin, Parser):
    @property
    def items(self):
        return self.root['data']

    def next_row(self):
        size = 1000
        skip = 0
        while True:
            params = {
                'size': size,
                'start': skip,
            }
            response = requests.get(self.url, params=params, auth=HTTPBasicAuth(self.user, self.password))
            if response.status_code != 200:
                raise GlobalImportError(_(u"Failed to download {url}. HTTP status code {status_code}").format(url=self.url, status_code=response.status_code))
            self.root = response.json()
            self.nb = int(self.root['metadata']['total'])
            for row in self.items:
                yield {self.normalize_field_name(src): val for src, val in row.iteritems()}
            skip += size
            if skip >= self.nb:
                return

    def filter_attachments(self, src, val):
        result = []
        for subval in val or []:
            try:
                name = subval['name']['fr']
            except KeyError:
                name = None
            result.append((subval['URL'], name, None))
        return result

    def normalize_field_name(self, name):
        return name


class OpenSystemParser(Parser):
    url = 'http://proxy-xml.open-system.fr/rest.aspx'

    def next_row(self):
        params = {
            'Login': self.login,
            'Pass': self.password,
            'Action': 'concentrateur_liaisons',
        }
        response = requests.get(self.url, params=params)
        if response.status_code != 200:
            raise GlobalImportError(_(u"Failed to download {url}. HTTP status code {status_code}").format(url=self.url, status_code=response.status_code))
        self.root = ET.fromstring(response.content).find('Resultat').find('Objets')
        self.nb = len(self.root)
        for row in self.root:
            id_sitra = row.find('ObjetCle').find('Cle').text
            for liaison in row.find('Liaisons'):
                yield {
                    'id_sitra': id_sitra,
                    'id_opensystem': liaison.find('ObjetOS').find('CodeUI').text,
                }

    def normalize_field_name(self, name):
        return name
