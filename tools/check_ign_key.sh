#!/usr/bin/env bash

referer=$1
key=$2

if test -z "$referer" -o -z "$key"; then
    echo Usage: $0 REFERER KEY
    exit 1
fi

layers_jpeg="GEOGRAPHICALGRIDSYSTEMS.MAPS GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN25TOUR SCAN100_PYR-JPEG_WLD_WM_WMTS_3D"

echo '------------------------------------------------------------'
echo GetCapabilities
curl -s -I --header "Referer: $referer" "https://data.geopf.fr/private/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetCapabilities&apikey=$key" | head -n 1

for layer in $layers_jpeg; do
    echo '------------------------------------------------------------'
    echo $layer
    curl -s -I --header "Referer: $referer" "https://data.geopf.fr/private/wmts?apikey=$key&LAYER=$layer&EXCEPTIONS=text/xml&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX=12&TILEROW=1478&TILECOL=2112" | head -n 1
done;
