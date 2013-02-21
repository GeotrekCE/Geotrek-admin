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

/**
 * Uniqify arrays
 * http://www.shamasis.net/2009/09/fast-algorithm-to-find-unique-items-in-javascript-array/
 */
Array.prototype.unique = function() {
    var o = {}, i, l = this.length, r = [];
    for(i=0; i<l;i+=1) o[this[i]] = this[i];
    for(i in o) r.push(o[i]);
    return r;
};


MapEntity.Context = new function() {
    var self = this;

    self.serializeFullContext = function(map, kwargs) {
        var context = {},
            filter = kwargs.filter,
            datatable = kwargs.datatable;
        
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

        // Mark timestamp
        context['timestamp'] = new Date().getTime();

        return JSON.stringify(context);
    },

    self.saveFullContext = function(map, kwargs) {
        var prefix = kwargs.prefix || '',
            serialized = self.serializeFullContext(map, kwargs);
        localStorage.setItem(prefix + 'map-context', serialized);
    };

    self.__loadFullContext = function(kwargs) {
        if (!kwargs) kwargs = {};
        var prefix = kwargs.prefix || '',
            context = localStorage.getItem(prefix + 'map-context');
        if (context)
            return JSON.parse(context);
        return null;
    };

    self.restoreLatestMapView = function (map, prefixes, kwargs) {
        var latest = null;
        for (var i=0; i<prefixes.length; i++) {
            var prefix = prefixes[i],
                context = self.__loadFullContext($.extend(kwargs, {prefix: prefix}));
            if (!latest || (context && context.timestamp && context.timestamp > latest.timestamp)) {
                latest = context;
                if (window.DEBUG) console.log(JSON.stringify(context));
            }
        }
        return self.restoreMapView(map, latest, kwargs);
    }

    self.restoreMapView = function(map, context, kwargs) {
        if (!context) context = self.__loadFullContext(kwargs);
        if (context && context.mapview) {
            map.setView(L.latLng(context.mapview.lat, context.mapview.lng), context.mapview.zoom);
            return true;
        }
        return false;
    };

    self.restoreFullContext = function(map, kwargs) {
        if (!kwargs) kwargs = {};
        var context = getURLParameter('context'),
            filter = kwargs.filter,
            datatable = kwargs.datatable,
            objectsname = kwargs.objectsname;
        if (context) {
            context = JSON.parse(context);
        }
        else {
            // If not received from URL, load from LocalStorage
            context = self.__loadFullContext(kwargs);
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

        self.restoreMapView(map, context, kwargs);
        
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
                    var p = layer.getLatLng(),
                        serialized = {lat: p.lat, lng: p.lng};
                    // In case the marker is snapped, serialize this information.
                    if (layer.snap) {
                        serialized['snap'] = layer.snap.properties.pk;
                    }
                    serialized = JSON.stringify(serialized);
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


MapEntity.History = L.Control.extend({

    saveListInfo: function (infos) {
        localStorage.setItem('list-search-results', JSON.stringify(infos));
    },

    remove: function (path) {
        $.post(window.SETTINGS.server + 'history/delete/', {path: path}, function() {
            var entries = $("#historylist > li")
              , entry = $("#historylist li a[href='" + path + "']").parents('li')
              , closeCurrent = String(window.location).indexOf(path, window.location.length - path.length) !== -1;
            if (closeCurrent) {
                // Closing current...
                if (entries.length > 2) {
                    // More left
                    entries.find(' > a').get(1).click();
                    $(entry).remove();
                }
                else {
                    // No more, redirect to list view 
                    window.location = '/';
                    $(entry).remove();
                }
            }
            else {
                $(entry).remove();
            }
        });
    },

    render: function () {
        var history = this;

        // Show number of results
        infos = localStorage.getItem('list-search-results') || "{nb: '?', model: null}";
        infos = JSON.parse(infos)
        $('#nbresults').text(infos.nb);
        $('#entitylist-dropdown').parent('li').addClass(infos.model);

        $('#historylist a').tooltip({'placement': 'bottom'});
        $('#historylist button.close').click(function (e) {
            e.preventDefault();
            var path = $(this).parents('a').attr('href');
            history.remove(path);
        });

        $('#historylist a').hoverIntent(
            function (e) {
                $(this).find('.close').removeClass('hidden');
                $(this).data('original-text', $(this).find('.content').text());
                var title = $(this).data('original-title');
                if (title)
                    $(this).find('.content').text(title);
            },
            function (e) {
                $(this).find('.content').text($(this).data('original-text'));
                $(this).find('.close').addClass('hidden');
            }
        );

        // Remove all entries returning 404 :) Useful to remove deleted entries
        $('#historylist li.history > a').each(function () {
            var path = $(this).attr('href');
            $.ajax({
                type: "HEAD",
                url: path,
                statusCode: {
                    404: function() {
                        history.remove(path);
                    }
                }
            });
        });
    },
});

MapEntity.history = new MapEntity.History();