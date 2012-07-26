/*
 * 
 * L'affiche des couches en WMS fonctionne.
 * Pour le tuilage, j'ai réussi en tatonnant à affichre des tuiles à un niveau de zoom précis (mais le callage n'était plus valide pour les autres niveaux
 * Donc je pense que la pyramide de tuiles est correcte, et que la clé réside en l'application de la bonne formule de transformation
 * 
 * 
 * */

var map;

$(function() {
    
    // On appelle le geojson en wgs84, Leaflet et proj4js s'occupent de faire la transformation
    $.getJSON('resources/rps-sentiers-wgs84.geojson', init_map_setup);
});

function init_map_setup(footpath_geojson_data) {

    // Scan 25, wms
    var wms_scan25 = new L.TileLayer.WMS("http://extranet.parcnational.fr/pnx/wms", {
        layers: 'scan25',
        format: 'image/png',
        transparent: true,
        attribution: "Ecrins",
        continuousWorld: true
    });

    // Scan 100, wms
    var wms_scan100 = new L.TileLayer.WMS("http://extranet.parcnational.fr/pnx/wms", {
        layers: 'scan100',
        format: 'image/png',
        transparent: true,
        attribution: "Ecrins",
        continuousWorld: true
    });
    
    // Couche sentier
    footpath_layer = new L.GeoJSON();
    footpath_layer.addData(footpath_geojson_data);

    // URL de la pyramide de tuile (ici qui pointe vers le tile cache, mais qui fonctionne également si on pointe juste sur le répertoire de cache)
    var mapUrl = 'http://localhost/cgi-bin/tilecache.cgi/1.0.0/scan100/{z}/{x}/{y}.png';
    var attrib = 'Ecrins';
    var tilelayer = new L.TileLayer(mapUrl, {
        //scheme: 'xyz'
        scheme: 'tms'
        ,maxZoom: 18
        ,minZoom: 0
        ,continuousWorld: true
        ,attribution: attrib
    });

    // Rappel des infos de Tilecache (génération de la pyramide)
    // Tilecache.cfg :
    /*[scan100]
    type=WMS
    url=http://extranet.parcnational.fr/pnx/wms
    layers=scan100
    extension=png
    debug=yes
    bbox=700000,6325197,1060000,6617738
        maxresolution:1142.7383
    srs=EPSG:2154
    #tms_type=google
    #resolutions= 1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192,16384,32768,65536,131072
    #resolutions= 1142.7383
    */
    
    var res = [131072, 65536, 32768, 16384, 8192, 4096, 2048, 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1];
    var start = new L.LatLng(44.818, 6.2993); // exprimé en lon/lat
    
    var map = new L.Map('map', {
        crs: L.CRS.proj4js('EPSG:2154'
            ,'+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs'
            , new L.Transformation(1 / 170000, -4.2588, -1 / 170000, 38.2579))
        ,scale: function(zoom) {
            return 1 / res[zoom];
        }
        ,continuousWorld: true
        ,'layers': [ 
                     //tilelayer , 
                     wms_scan25,
                     wms_scan100,
                     new L.Marker(start, { title: 'Test' })
                   ]
        //,scheme: 'xyz'
        ,center: start
        ,zoom : 5
        }
    );
    
    var baseLayers = { "Tile" : tilelayer, "Scan25": wms_scan25,"Scan100": wms_scan100};
    var overlays = { "troncons": footpath_layer };

    layersControl = new L.Control.Layers(baseLayers, overlays);
    map.addControl(layersControl);
    
    map.on('mousemove', function(e) {
        document.getElementById("infos").innerHTML = e.latlng + " - Zoom = " + map.getZoom();
    });

    map.on('click', function(e) {
        var marker = new L.Marker(e.latlng);
        map.addLayer(marker);
    });

    
}
