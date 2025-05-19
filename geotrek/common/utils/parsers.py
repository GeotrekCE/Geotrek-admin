import codecs
import os
from datetime import datetime
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import MultiLineString
from django.utils.translation import gettext as _

from geotrek.common.utils.file_infos import get_encoding_file


class GeomValueError(Exception):
    pass


def add_http_prefix(url):
    if url.startswith("http"):
        return url
    else:
        return "http://" + url


def maybe_fix_encoding_to_utf8(file_name):
    encoding = get_encoding_file(file_name)

    # If not utf-8, convert file to utf-8
    if encoding != "utf-8":
        tmp_file_path = os.path.join(
            settings.TMP_DIR, "fileNameTmp_" + str(datetime.now().timestamp())
        )
        BLOCKSIZE = 9_048_576
        with codecs.open(file_name, "r", encoding) as sourceFile:
            with codecs.open(tmp_file_path, "w", "utf-8") as targetFile:
                while True:
                    contents = sourceFile.read(BLOCKSIZE)
                    if not contents:
                        break
                    targetFile.write(contents)
        os.replace(tmp_file_path, file_name)
    return file_name


def get_geom_from_gpx(data):
    def convert_to_geos(geom):
        # FIXME: is it right to try to correct input geometries?
        # FIXME: how to log that info/spread errors?
        if geom.geom_type == "MultiLineString" and any(
            [ls for ls in geom if ls.num_points == 1]
        ):
            # Handles that framework conversion fails when there are LineStrings of length 1
            geos_mls = MultiLineString([ls.geos for ls in geom if ls.num_points > 1])
            geos_mls.srid = geom.srid
            return geos_mls

        return geom.geos

    def get_layer(datasource, layer_name):
        for layer in datasource:
            if layer.name == layer_name:
                return layer

    def maybe_get_linestring_from_layer(layer):
        if layer.num_feat == 0:
            return None
        geoms = []
        for feat in layer:
            if feat.geom.num_coords == 0:
                continue
            geos = convert_to_geos(feat.geom)
            if geos.geom_type == "MultiLineString":
                geos = (
                    geos.merged
                )  # If possible we merge the MultiLineString into a LineString
                if geos.geom_type != "LineString":
                    raise GeomValueError(
                        _(
                            "Feature geometry cannot be converted to a single continuous LineString feature"
                        )
                    )
            geoms.append(geos)

        full_geom = MultiLineString(geoms)
        full_geom.srid = geoms[0].srid
        full_geom = (
            full_geom.merged
        )  # If possible we merge the MultiLineString into a LineString
        if full_geom.geom_type != "LineString":
            raise GeomValueError(
                _(
                    "Geometries from various features cannot be converted to a single continuous LineString feature"
                )
            )

        return full_geom

    """Given GPX data as bytes it returns a geom."""
    # FIXME: is there another way than the temporary file? It seems not. `DataSource` really expects a filename.
    with NamedTemporaryFile(mode="w+b", dir=settings.TMP_DIR) as ntf:
        ntf.write(data)
        ntf.flush()

        file_path = maybe_fix_encoding_to_utf8(ntf.name)
        ds = DataSource(file_path)
        for layer_name in ("tracks", "routes"):
            layer = get_layer(ds, layer_name)
            geos = maybe_get_linestring_from_layer(layer)
            if geos:
                break
        else:
            msg = "No LineString feature found in GPX layers tracks or routes"
            raise GeomValueError(msg)
        geos.transform(settings.SRID)
        return geos


def get_geom_from_kml(data):
    """Given KML data as bytes it returns a geom."""

    def get_geos_linestring(datasource):
        layer = datasource[0]
        geom = get_first_geom_with_type_in(
            types=["MultiLineString", "LineString"], geoms=layer.get_geoms()
        )
        geom.coord_dim = 2
        geos = geom.geos
        if geos.geom_type == "MultiLineString":
            geos = (
                geos.merged
            )  # If possible we merge the MultiLineString into a LineString
            if geos.geom_type != "LineString":
                raise GeomValueError(
                    _(
                        "Feature geometry cannot be converted to a single continuous LineString feature"
                    )
                )
        return geos

    def get_first_geom_with_type_in(types, geoms):
        for g in geoms:
            for t in types:
                if g.geom_type.name.startswith(t):
                    return g
        msg = "The attached KML geometry does not have any LineString or MultiLineString data"
        raise GeomValueError(msg)

    with NamedTemporaryFile(mode="w+b", dir=settings.TMP_DIR) as ntf:
        ntf.write(data)
        ntf.flush()

        file_path = maybe_fix_encoding_to_utf8(ntf.name)
        ds = DataSource(file_path)
        geos = get_geos_linestring(ds)
        geos.transform(settings.SRID)
        return geos
