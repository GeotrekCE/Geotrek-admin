var map;


$(function() {
    
    //$.getJSON('resources/rps-sentiers-lambert93.geojson', init_map_setup);
    $.getJSON('resources/rps-sentiers-wgs84.geojson', init_map_setup);
});

function init_map_setup(footpath_geojson_data) {

    var wms_scan25 = new L.TileLayer.WMS("http://extranet.parcnational.fr/pnx/wms", {
        layers: 'scan25',
        format: 'image/png',
        transparent: true,
        attribution: "Ecrins",
        continuousWorld: true
    });

   var wms_scan100 = new L.TileLayer.WMS("http://extranet.parcnational.fr/pnx/wms", {
        layers: 'scan100',
        format: 'image/png',
        transparent: true,
        attribution: "Ecrins",
        continuousWorld: true
    });
    
    footpath_layer = new L.GeoJSON();
    footpath_layer.addData(footpath_geojson_data);

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

    // Tilecache.cfg :
    // 700000,6325197,1060000,6617738
    // 1142.7383

    // L93 to 4326, on convertit l'origine pour voir
    // 700000 , 6325197   => 3.0000000000000004 , 44.0257746719149
    
    
    var res = [131072, 65536, 32768, 16384, 8192, 4096, 2048, 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1, 0.5, 0.25];
    var start = new L.LatLng(44.818, 6.2993);
    var map = new L.Map('map', {
        crs: L.CRS.proj4js('EPSG:2154'
            ,'+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs'
            //,new L.Transformation(1, 0, -1, 0))
            //,new L.Transformation(1, 0, 1, 0))
            //,new L.Transformation(1, 700000, -1, 6600000))
            //,new L.Transformation(1, 700000, 1, -6600000))
            //,new L.Transformation(1, -997000, -1, 6460000))
            //, new L.Transformation(1 / 360, 0.5, -1 / 360, 0.5))
            //, new L.Transformation(1 / 20000, 700000, -1 / 20000, 6617738))
            //, new L.Transformation(1 / 170000, -4.2588, -1 / 170000, 38.2579))
            //, new L.Transformation(1 / 170000, 3.0000000000000004, -1 / 170000, 44.0257746719149))
            , new L.Transformation(1 / 1142.7383, 3.0000000000000004, -1 / 1142.7383, 44.0257746719149))            

        ,scale: function(zoom) {
            return 1 / res[zoom];
        }
        ,continuousWorld: true
        ,'layers': [ 
                     tilelayer , 
                     //wms_scan25,
                     //wms_scan100,
                     new L.Marker(start, { title: 'Test' })
                   ]
        ,scheme: 'wms'
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
