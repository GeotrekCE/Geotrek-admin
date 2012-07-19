var map;


$(function() {
    
    $.getJSON('resources/rps-sentiers-lambert93.geojson', init_map_setup);
    //$.getJSON('resources/rps-sentiers-wgs84.geojson', init_map_setup);
});

/*function init() {
    $.getJSON('resources/rps-sentiers-lambert93.geojson', init_map_setup);
    init_map_setup();
}*/

function init_map_setup(footpath_geojson_data) {

    
    // layers //
   var wms_scan25 = new L.TileLayer.WMS("http://extranet.parcnational.fr/pnx/wms", {
        layers: 'scan25',
        format: 'image/png',
        transparent: true,
        attribution: "Ecrins",
        continuousWorld: true
    });


    
    
    /*
    // http://geobi.makina-corpus.net/livembtiles/PNE_16042012_4/11/1059/737.png
    var tilelayer_url = 'http://geobi.makina-corpus.net/livembtiles/PNE_16042012_4/{z}/{x}/{y}.png';
    var tilelayer = new L.TileLayer(tilelayer_url, {
         'minZoom': 10
    });

    /*
    // map //

    // http://geobi.makina-corpus.net/livembtiles/PNE_16042012_4.jsonp
    var southWest = new L.LatLng(44.3788, 5.7651)
      , northEast = new L.LatLng(45.2498, 6.7072)
      , bounds = new L.LatLngBounds(southWest, northEast)
      , center = new L.LatLng(44.8189, 6.2993) // bounds.getCenter()
      , zoom = 12
    ;

    map = new L.Map('map', {
        'center': center
      , 'zoom': zoom
      , 'layers': [ footpath_layer, tilelayer , wms_scan25]
    });


    var baseLayers = { "base": tilelayer};
    var overlays = { "troncons": footpath_geojson_data, "scan25" : wms_scan25 };

    layersControl = new L.Control.Layers(baseLayers, overlays);
    map.addControl(layersControl);    
    
    
    
    
    return;
    */
    
    
    
    
    footpath_layer = new L.GeoJSON();
    footpath_layer.addData(footpath_geojson_data);

    
    /*
    // http://geobi.makina-corpus.net/livembtiles/PNE_16042012_4.jsonp
    var center = new L.LatLng(44.8189, 6.2993);
    var zoom = 12;

    map = new L.Map('map', {
        crs: L.CRS.proj4js('EPSG:2154'
        ,'+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs'
        ,new L.Transformation(1, 0, -1, 0)),
        'center': center,
       'zoom': zoom,
       'layers': [ tilelayer, footpath_layer]  
    });

    var baseLayers = { "base": tilelayer };
    var overlays = { "troncons": footpath_layer };

    layersControl = new L.Control.Layers(baseLayers, overlays);
    map.addControl(layersControl);
    */

    var mapUrl = 'http://localhost/cgi-bin/tilecache.cgi/1.0.0/scan25/{z}/{x}/{y}.png';
    var attrib = 'Ecrins';
    var tilelayer = new L.TileLayer(mapUrl, {
        //scheme: 'xyz'
        scheme: 'tms'
        ,maxZoom: 18
        ,minZoom: 0
        ,continuousWorld: true
        ,attribution: attrib
    });

    //var res = [90, 50, 30, 15, 7.5, 4, 2, 1, 0.5, 0.2] ;
    //var res = [8192, 4096, 2048, 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1, 0.5];
    var res = [131072, 65536, 32768, 16384, 8192, 4096, 2048, 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1, 0.5, 0.25];
    //var res = [100000000, 65536000, 3276800, 16384, 8192, 4096, 2048, 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1, 0.5, 0.25];
    var start = new L.LatLng(44.818, 6.2993);
    var map = new L.Map('map', {
        crs: L.CRS.proj4js('EPSG:2154'
            ,'+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs'
            ,new L.Transformation(1, 0, -1, 0))
            //,new L.Transformation(1, 0, 1, 0))
            //,new L.Transformation(1, 700000, -1, 6600000))
            //,new L.Transformation(1, 700000, 1, -6600000))

        ,scale: function(zoom) {
            return 1 / res[zoom];
        }
        ,continuousWorld: false
        //,'layers': [ wms_scan25 , tilelayer]
        ,'layers': [ //tilelayer , 
                     wms_scan25, 
                     new L.Marker(new L.LatLng(44.818, 6.2993), {
                        title: 'Test'
                        })
                   ]
        ,scheme: 'wms'
        ,center: start
        ,zoom : 0
        }
    );
    
    var baseLayers = { "Tile" : tilelayer, "Scan25": wms_scan25};
    var overlays = { "troncons": footpath_layer };

    layersControl = new L.Control.Layers(baseLayers, overlays);
    map.addControl(layersControl);
    
    
    //map.setView(start, 0);
    
    // xmin = 921000 ; xmax = 997000 ; ymin = 6325000 ; ymax = 6460000

    /*var map = new L.Map('map', {
        crs:  L.CRS.proj4js('EPSG:2154', '+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs', new L.Transformation(1, 0, -1, 0)),
        scale: function(zoom) {
            return 1 / (234.375 / Math.pow(2, zoom));
        },
        layers: [
            new L.TileLayer('http://localhost/cgi-bin/tilecache.cgi/1.0.0/scan25/{z}/{x}/{y}.png', {
            //minZoom: 0,
            //maxZoom: 4,
            continuousWorld: true
            }), 
            new L.Marker(new L.LatLng(44.8189, 6.2993), {
            title: 'Galdhøpiggen 2469 m'
            })
        ],
    
    center: new L.LatLng(44.8189, 6.2993),
    zoom: 3,
    continuousWorld: true
    });
    */
    
    //alert(map.getBounds());
    var southWest = new L.LatLng(44.3788, 5.7651)
      , northEast = new L.LatLng(45.2498, 6.7072)
      , bounds = new L.LatLngBounds(southWest, northEast)
    ;    

    map.on('mousemove', function(e) {
        document.getElementById("infos").innerHTML = e.latlng + " - Zoom = " + map.getZoom();
    });




}
