if (!MapEntity) var MapEntity = {};

L.Control.Screenshot = L.Control.extend({
    includes: L.Mixin.Events,
    options: {
        position: 'topleft',
        title: 'Screenshot',
    },
    
    screenshot: function () {
        // Screenshot effect
        $('<div id="overlay" style="position:fixed; top:0; left:0; width:100%; height:100%; background-color: white;"> </div>')
            .appendTo(document.body)
            .fadeOut();
        this.fire('trigger');
    },

    onAdd: function(map) {
        this.map = map;
        this._container = L.DomUtil.create('div', 'leaflet-control-zoom leaflet-control');
        var link = L.DomUtil.create('a', 'leaflet-control-zoom-out screenshot-control', this._container);
        link.href = '#';
        link.title = this.options.title;

        L.DomEvent
            .addListener(link, 'click', L.DomEvent.stopPropagation)
            .addListener(link, 'click', L.DomEvent.preventDefault)
            .addListener(link, 'click', this.screenshot, this);
        return this._container;
    }
});



/**
 * Get URL parameter in Javascript
 * source: http://stackoverflow.com/questions/1403888/get-url-parameter-with-jquery
 */
function getURLParameter(name) {
    var paramEncoded = (RegExp('[?|&]' + name + '=' + '(.+?)(&|$)').exec(location.search)||[,null])[1],
        paramDecoded = decodeURIComponent(paramEncoded);
    return paramDecoded == 'null' ? null : paramDecoded;
}


MapEntity.Context = new function() {
    var self = this;

    self.serializeFullContext = function(map, filter, datatable) {
        var context = {};
        
        // Map view
        context['mapview'] = {'lat': map.getCenter().lat, 'lng': map.getCenter().lng, 'zoom': map.getZoom()};
        
        // layers shown by name
        var layers = [];
        $('form.leaflet-control-layers-list input:checked').each(function () {
            layers.push($.trim($(this).parent().text()));
        });
        context['maplayers'] = layers;
        
        // Form filters
        if (filter) {
            // exclude bbox field, since it comes from the map view.
            var fields = $($(filter).serializeArray()).filter(function (){ return this.name != 'bbox'});
            context['filter'] = $.param(fields);
        }
        
        // Sort columns
        if (datatable) {
            context['sortcolumns'] = datatable.fnSettings().aaSorting;
        }
        
        // Extra-info, not restored so far but can be useful for screenshoting
        context['url'] = window.location.toString();
        context['viewport'] = {'width': $(window).width(), 'height': $(window).height()};
        context['mapsize'] = {'width': $('.map-panel').width(), 'height': $('.map-panel').height()};

        return JSON.stringify(context);
    },

    self.saveFullContext = function(map, filter, datatable) {
        var serialized = self.serializeFullContext(map, filter, datatable);
        localStorage.setItem('map-context', serialized);
    };

    self.__loadFullContext = function() {
        var context = localStorage.getItem('map-context');
        if (context)
            return JSON.parse(context);
        return null;
    };

    self.restoreMapView = function(map, context) {
        if (!context) context = self.__loadFullContext();
        if (context && context.mapview) {
            map.setView(L.latLng(context.mapview.lat, context.mapview.lng), context.mapview.zoom);
            return true;
        }
        return false;
    };

    self.restoreFullContext = function(map, filter, datatable, objectsname) {
        var context = getURLParameter('context');
        if (context) {
            context = JSON.parse(context);
        }
        else {
            // If not received from URL, load from LocalStorage
            context = self.__loadFullContext();
        }
        if (!context) {
            console.warn("No context found.");
            map.fitBounds(map.options.maxBounds);
            return;  // No context, no restore.
        }
        
        if (context.print) {
            // Hide controls
            $('.leaflet-control').hide();   // Hide all
            $('.leaflet-control-scale').show(); // Show scale
            $(map._container).removeClass('leaflet-fade-anim');
        }

        self.restoreMapView(map, context);
        
        if (filter && context.filter) {
            $(filter).deserialize(context.filter);
        }
        if (datatable && context.sortcolumns) {
            datatable.fnSort(context.sortcolumns);
        }
        // Show layers by their name
        if (context.maplayers) {
            var layers = context.maplayers;
            layers.push(objectsname);
            $('form.leaflet-control-layers-list input').each(function () {
                if ($.trim($(this).parent().text()) != objectsname) {
                    $(this).removeAttr('checked');
                }
            });
            for(var i=0; i<layers.length; i++) {
                var layer = layers[i];
                $('form.leaflet-control-layers-list input').each(function () {
                    if ($.trim($(this).parent().text()) == layer) {
                        $(this).attr('checked', 'checked');
                    }
                });
            }
            map.layerscontrol._onInputClick();
        }
    };
};


MapEntity.makeGeoFieldProxy = function($field, layer) {
    // Proxy to field storing WKT. It also stores the matching layer.
    var _current_layer = layer || null,
        topologyMode = false;

    return {
        setTopologyMode: function(state) {
            topologyMode = state;
        },
        // If topologyMode, store WKT
        // Else store the given parameter using JSON.stringify
        storeLayerGeomInField: function(layer) {
            var old_layer = _current_layer;
            _current_layer = layer;

            var serialized = '';
            if (topologyMode) {
                if (layer instanceof L.Marker) {
                    var p = layer.getLatLng();
                    serialized = JSON.stringify({lat: p.lat, lng: p.lng});
                }
                else
                    serialized = JSON.stringify(layer);
            }
            else {
                if (layer) serialized = L.Util.getWKT(layer);
            }
            $field.val(serialized);
            return old_layer;
        },
        getLayer: function () {
            return _current_layer;
        },
        getSerialized: function() {
            return $field.val();
        }
    };
};

MapEntity.showNumberSearchResults = function (nb) {
    if (arguments.length > 0) {
        localStorage.setItem('list-search-results', nb);
    }
    else {
        nb = localStorage.getItem('list-search-results') || '?';
    }
    $('#nbresults').text(nb);
}
