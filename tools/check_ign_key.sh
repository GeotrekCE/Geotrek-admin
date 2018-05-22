#!/usr/bin/env bash

referer=$1
key=$2
layers_jpeg="GEOGRAPHICALGRIDSYSTEMS.MAPS GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN-EXPRESS.CLASSIQUE GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN-EXPRESS.STANDARD ORTHOIMAGERY.ORTHOPHOTOS"
layers_png="CADASTRALPARCELS.PARCELS"

for layer in $layers_jpeg; do
    echo '------------------------------------------------------------'
    echo $layer
    curl -s -I --header "Referer: $referer" "http://gpp3-wxs.ign.fr/$key/geoportail/wmts?LAYER=$layer&EXCEPTIONS=text/xml&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX=12&TILEROW=1478&TILECOL=2112" | head -n 1
done;

for layer in $layers_png; do
    echo '------------------------------------------------------------'
    echo $layer
    curl -s -I --header "Referer: $referer" "http://gpp3-wxs.ign.fr/$key/geoportail/wmts?LAYER=$layer&EXCEPTIONS=text/xml&FORMAT=image/png&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX=12&TILEROW=1478&TILECOL=2112" | head -n 1
done;
