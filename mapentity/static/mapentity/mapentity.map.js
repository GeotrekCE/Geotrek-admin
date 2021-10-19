L.Control.Screenshot = L.Control.extend({
    includes: L.Mixin.Events,
    options: {
        position: 'topleft',
    },
    statics: {
        TITLE:  'Screenshot'
    },

    initialize: function (url, getcontext) {
        this.url = url;
        this.getcontext = getcontext;
    },

    screenshot: function () {
        // Screenshot effect
        $('<div id="overlay" style="z-index: 5000; position:fixed; top:0; left:0; width:100%; height:100%; background-color: white;"> </div>')
            .appendTo(document.body)
            .fadeOut();

        var fullContext = this.getcontext();
        // Hack to download response attachment in Ajax
        $('<form action="' + this.url + '" method="post">' +
        '<textarea name="printcontext">' + fullContext + '</textarea>' +
        '</form>').appendTo('body').submit().remove();
        this.fire('triggered');
    },

    onAdd: function(map) {
        this.map = map;
        this._container = L.DomUtil.create('div', 'leaflet-control-zoom leaflet-control leaflet-bar');
        var link = L.DomUtil.create('a', 'leaflet-control-zoom-out screenshot-control', this._container);
        link.href = '#';
        link.title = L.Control.Screenshot.TITLE;

        L.DomEvent
            .addListener(link, 'click', L.DomEvent.stopPropagation)
            .addListener(link, 'click', L.DomEvent.preventDefault)
            .addListener(link, 'click', this.screenshot, this);
        return this._container;
    }
});


/**
 * Shows a static label in the middle of the Polyline.
 * It will be hidden on zoom levels below ``LABEL_MIN_ZOOM``.
 */
MapEntity.showLineLabel = function (layer, options) {
    var LABEL_MIN_ZOOM = 6;

    var rgb = parseColor(options.color);

    layer.bindLabel(options.text, {noHide: true, className: options.className});

    var __layerOnAdd = layer.onAdd;
    layer.onAdd = function (map) {
        __layerOnAdd.call(layer, map);
        if (map.getZoom() >= LABEL_MIN_ZOOM) {
            layer._showLabel();
        }
        map.on('zoomend', hideOnZoomOut);
    };

    var __layerOnRemove = layer.onRemove;
    layer.onRemove = function () {
        layer._map.off('zoomend', hideOnZoomOut);
        if (layer._hideLabel) layer._hideLabel();
        __layerOnRemove.call(layer);
    };

    var __layerShowLabel = layer._showLabel;
    layer._showLabel = function () {
        __layerShowLabel.call(layer, {latlng: midLatLng(layer)});
        layer.label._container.title = options.title;
        layer.label._container.style.backgroundColor = 'rgba('+rgb.join(',')+ ',0.8)';
        layer.label._container.style.borderColor = 'rgba('+rgb.join(',')+ ',0.6)';
    };

    function hideOnZoomOut() {
        if (layer._map.getZoom() < LABEL_MIN_ZOOM)
            if (layer._hideLabel) layer._hideLabel();
        else
            if (layer._showLabel) layer._showLabel();
    }

    function midLatLng(line) {
        var mid = Math.floor(line.getLatLngs().length/2);
        return L.latLng(line.getLatLngs()[mid]);
    }
};


$(window).on('entity:map', function (e, data) {
    var map = data.map,
        $container = $(map._container),
        readonly = $container.data('readonly');

    // Replace default layer switcher with Leaflet.GroupedLayerSwitcher
    if (map.layerscontrol) {
        map.layerscontrol.removeFrom(map);
    }
    var baseLayers = {};
    var overlaysLayers = {};
    for (var l in map.layerscontrol._layers) {
        var layer = map.layerscontrol._layers[l];
        if (layer.overlay)
            overlaysLayers[layer.name] = layer.layer;
        else
            baseLayers[layer.name] = layer.layer;
    }
    var layerscontrol = L.control.groupedLayers(baseLayers, {'': overlaysLayers});
    map.layerscontrol = layerscontrol.addTo(map);

    if (readonly) {
        // Set map readonly
        map.dragging.disable();
        map.touchZoom.disable();
        map.doubleClickZoom.disable();
        map.scrollWheelZoom.disable();
        map.boxZoom.disable();
    }

    map.attributionControl.setPrefix('');

    var mapBounds = $container.data('mapextent');
    if (mapBounds) {
        map.fitBounds(mapBounds);
        var maxZoom = $container.data('fitmaxzoom');
        if (map.getZoom() > maxZoom) {
            console.log('Limited zoom to ', maxZoom, '. Was ', map.getZoom());
            map.setZoom(maxZoom);
        }
        map.resetviewControl.getBounds = function () { return mapBounds; };
    }

    map.addControl(new L.Control.FullScreen());
    map.addControl(new L.Control.MeasureControl());
});


$(window).on('entity:map:detail', function (e, data) {
    var map = data.map,
        $container = $(map._container);

    // Map screenshot button
    var screenshot = new L.Control.Screenshot(window.SETTINGS.urls.screenshot, function () {
        context = MapEntity.Context.getFullContext(map);
        context['selector'] = '#detailmap';
        return JSON.stringify(context);
    });
    map.addControl(screenshot);

    // Restore map context, only for screenshoting purpose
    var context = getURLParameter('context');
    if (context && typeof context == 'object') {
        MapEntity.Context.restoreFullContext(map, context);
    }

    // Save map context : will be restored on next form (e.g. interventions, ref story #182)
    $(window).unload(function () {
        MapEntity.Context.saveFullContext(map, {prefix: 'detail'});
    });

    // Show object geometry in detail map
    var $singleObject = $container.find('.geojsonfeature'),
        objectLayer = null;
    if ($singleObject.length > 0) {
        objectLayer = _showSingleObject(JSON.parse($singleObject.text()));
    }

    $(window).trigger('detailmap:ready', {map: map,
                                          layer: objectLayer,
                                          context: context,
                                          modelname: data.modelname});


    function _showSingleObject(geojson) {
        var DETAIL_STYLE = L.Util.extend(window.SETTINGS.map.styles.detail, {clickable: false});

        // Apparence of geometry for export can be controlled via setting
        if (context && context.print) {
            var specified = window.SETTINGS.map.styles.print[data.modelname];
            if (specified) {
                DETAIL_STYLE = L.Util.extend(DETAIL_STYLE, specified);
            }
        }

        // Add layers
        var objectLayer = new L.ObjectsLayer(geojson, {
            style: DETAIL_STYLE,
            indexing: false,
            modelname: data.modelname
        });
        map.addLayer(objectLayer);
        map.on('layeradd', function (e) {
            if (!e.layer.properties && objectLayer._map) {
                objectLayer.bringToFront();
            }
        });

        // Show objects enumeration
        var sublayers = objectLayer.getLayers();
        if (sublayers.length === 1) {
            // Single layer, but multi-* or geometrycollection
            if (typeof sublayers[0].getLayers === 'function') {
                sublayers[0].showEnumeration();
            }
        }
        else {
            objectLayer.showEnumeration();
        }

        return objectLayer;
    }
});


$(window).on('entity:map:list', function (e, data) {
    var map = data.map,
        bounds = L.latLngBounds(data.options.extent);

    map.removeControl(map.attributionControl);
    map.doubleClickZoom.disable();

    map.addControl(new L.Control.Information());
    map.addControl(new L.Control.ResetView(bounds));

    /*
     * Objects Layer
     * .......................
     */
    function getUrl(properties, layer) {
        return window.SETTINGS.urls.detail.replace(new RegExp('modelname', 'g'), data.modelname)
                                          .replace('0', properties.pk);
    }
    if (typeof window.SETTINGS.map.styles.others === "function"){
        var style = window.SETTINGS.map.styles.others;
    }
    else{
        var style = L.Util.extend({}, window.SETTINGS.map.styles.others);
    }
    var objectsLayer = new L.ObjectsLayer(null, {
        objectUrl: getUrl,
        style: style,
        modelname: data.modelname,
        onEachFeature: function (geojson, layer) {
            if (geojson.properties.name) layer.bindLabel(geojson.properties.name);
        }
    });
    objectsLayer.on('highlight select', function (e) {
        if (data.modelname != 'site' && e.layer._map !== null) e.layer.bringToFront();
    });

    map.addLayer(objectsLayer);
    objectsLayer.load(window.SETTINGS.urls.layer.replace(new RegExp('modelname', 'g'), data.modelname));

    var nameHTML = '<span style="color: '+ style['color'] + ';">&#x25A3;</span>&nbsp;' + data.objectsname;
    map.layerscontrol.addOverlay(objectsLayer, nameHTML, tr("Objects"));

    var dt = MapEntity.mainDatatable;

    /*
     * Assemble components
     * .......................
     */
    var mapsync = new L.MapListSync(dt,
                                    map,
                                    objectsLayer, {
                                        filter: {
                                            form: $('#mainfilter'),
                                            submitbutton: $('#filter'),
                                            resetbutton: $('#reset'),
                                            bboxfield: $('#id_bbox'),
                                        }
                                    });
    mapsync.on('reloaded', function (data) {
        // Show and save number of results
        MapEntity.history.saveListInfo({model: data.modelname,
                                        nb: data.nbrecords});
        // Show layer info
        objectsLayer.fire('info', {info : (data.nbrecords + ' ' + tr("results"))});
    });

    // Main filter
    var t = new MapEntity.TogglableFilter();
    mapsync.on('reloaded', function (data) {
        t.setsubmit();
    });

    // Map screenshot button
    var screenshot = new L.Control.Screenshot(window.SETTINGS.urls.screenshot, function () {
        context = MapEntity.Context.getFullContext(map, {
            filter: '#mainfilter',
            datatable: dt
        });
        context['selector'] = '#mainmap';
        return JSON.stringify(context);
    });
    map.addControl(screenshot);

    /*
     * Allow to load files locally.
     */
    var pointToLayer = function (feature, latlng) {
            return L.circleMarker(latlng, {style: window.SETTINGS.map.styles.filelayer})
                    .setRadius(window.SETTINGS.map.styles.filelayer.radius);
        },
        onEachFeature = function (feature, layer) {
            if (feature.properties.name) {
                layer.bindLabel(feature.properties.name);
            }
        },
        filecontrol = L.Control.fileLayerLoad({
            fitBounds: true,
            layerOptions: {style: window.SETTINGS.map.styles.filelayer,
                           pointToLayer: pointToLayer,
                           onEachFeature: onEachFeature}
        });
    map.filecontrol = filecontrol;
    map.addControl(filecontrol);

    // Restore map view, layers and filter from any available context
    // Get context from URL parameter, if any
    var mapViewContext = getURLParameter('context'),
        layerLabel = $('<div></div>').append(nameHTML).text();
    MapEntity.Context.restoreFullContext(map,
        // From URL param
        mapViewContext,
        // Parameters
        {
            filter: '#mainfilter',
            datatable: dt,
            objectsname: layerLabel,
            // We can have several contexts in the application (mainly 'detail' and 'list')
            // Using prefixes is a way to manage this.
            prefix: 'list',
        }
    );
    $(window).unload(function () {
        MapEntity.Context.saveFullContext(map, {
            filter: '#mainfilter',
            datatable: dt,
            prefix: 'list',
        });
    });
});
