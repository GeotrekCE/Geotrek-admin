from typing import Dict

import fiona


def update_gis(input_file_path: str, output_file_path: str, new_properties: Dict):
    '''
    Utility function that reads a GIS file (GeoPackage or Shapefile), update some properties,
    then write a new shapefile (typically in /tmp). Useful to test specific property values.
    '''

    with fiona.open(input_file_path) as source:
        with fiona.open(output_file_path,
                        mode='w',
                        crs=source.crs,
                        driver=source.driver,
                        schema=source.schema) as dest:
            for feat in source:
                dest.write(fiona.Feature(
                    geometry=feat.geometry,
                    properties={**feat.properties, **new_properties}
                ))
