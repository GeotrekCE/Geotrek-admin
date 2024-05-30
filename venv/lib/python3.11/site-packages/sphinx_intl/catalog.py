# -*- coding: utf-8 -*-

import os
import io

from babel.messages import pofile, mofile


def load_po(filename, **kwargs):
    """read po/pot file and return catalog object

    :param unicode filename: path to po/pot file
    :param kwargs: keyword arguments to forward to babel's read_po call
    :return: catalog object
    """
    # pre-read to get charset
    with io.open(filename, 'rb') as f:
        cat = pofile.read_po(f)
    charset = cat.charset or 'utf-8'

    # To decode lines by babel, read po file as binary mode and specify charset for
    # read_po function.
    with io.open(filename, 'rb') as f:  # FIXME: encoding VS charset
        return pofile.read_po(f, charset=charset, **kwargs)


def dump_po(filename, catalog, **kwargs):
    """write po/pot file from catalog object

    :param unicode filename: path to po file
    :param catalog: catalog object
    :param kwargs: keyword arguments to forward to babel's write_po call; also
                    accepts a deprecated `line_width` option to forward to
                    write_po's `width` option
    :return: None
    """
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    # (compatibility) line_width was the original argument used to forward
    # line width hints into write_po's `width` argument; if provided,
    # set/override the width value
    if 'line_width' in kwargs:
        kwargs['width'] = kwargs['line_width']
        del kwargs['line_width']

    # Because babel automatically encode strings, file should be open as binary mode.
    with io.open(filename, 'wb') as f:
        pofile.write_po(f, catalog, **kwargs)


def write_mo(filename, catalog, **kwargs):
    """write mo file from catalog object

    :param unicode filename: path to mo file
    :param catalog: catalog object
    :return: None
    """
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with io.open(filename, 'wb') as f:
        mofile.write_mo(f, catalog, **kwargs)


def translated_entries(catalog):
    return [m for m in catalog if m.id and m.string]


def fuzzy_entries(catalog):
    return [m for m in catalog if m.id and m.fuzzy]


def untranslated_entries(catalog):
    return [m for m in catalog if m.id and not m.string]


def update_with_fuzzy(catalog, catalog_source):
    """update catalog by template catalog with fuzzy flag.

    :param catalog: catalog object to be updated
    :param catalog_source: catalog object as a template to update 'catalog'
    :return: None
    """
    catalog.update(catalog_source)
