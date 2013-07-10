if (!MapEntity) var MapEntity = {};

L.Control.Screenshot = L.Control.extend({
    includes: L.Mixin.Events,
    options: {
        position: 'topleft',
        title: 'Screenshot'
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
    if (typeof paramDecoded == 'string') {
        try {
            return JSON.parse(paramDecoded);
        }
        catch (e) {}
    }
    return paramDecoded;
}


/**!
 * @preserve parseColor
 * Copyright 2011 THEtheChad Elliott
 * Released under the MIT and GPL licenses.
 */
// Parse hex/rgb{a} color syntax.
// @input string
// @returns array [r,g,b{,o}]
parseColor = function(color) {

    var cache
      , p = parseInt // Use p as a byte saving reference to parseInt
      , color = color.replace(/\s\s*/g,'') // Remove all spaces
    ;//var
    
    // Checks for 6 digit hex and converts string to integer
    if (cache = /^#([\da-fA-F]{2})([\da-fA-F]{2})([\da-fA-F]{2})/.exec(color)) 
        cache = [p(cache[1], 16), p(cache[2], 16), p(cache[3], 16)];
        
    // Checks for 3 digit hex and converts string to integer
    else if (cache = /^#([\da-fA-F])([\da-fA-F])([\da-fA-F])/.exec(color))
        cache = [p(cache[1], 16) * 17, p(cache[2], 16) * 17, p(cache[3], 16) * 17];
        
    // Checks for rgba and converts string to
    // integer/float using unary + operator to save bytes
    else if (cache = /^rgba\(([\d]+),([\d]+),([\d]+),([\d]+|[\d]*.[\d]+)\)/.exec(color))
        cache = [+cache[1], +cache[2], +cache[3], +cache[4]];
        
    // Checks for rgb and converts string to
    // integer/float using unary + operator to save bytes
    else if (cache = /^rgb\(([\d]+),([\d]+),([\d]+)\)/.exec(color))
        cache = [+cache[1], +cache[2], +cache[3]];
        
    // Otherwise throw an exception to make debugging easier
    else throw Error(color + ' is not supported by parseColor');
    
    // Performs RGBA conversion by default
    isNaN(cache[3]) && (cache[3] = 1);
    
    // Adds or removes 4th value based on rgba support
    // Support is flipped twice to prevent erros if
    // it's not defined
    return cache.slice(0,3 + !!$.support.rgba);
}


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
        layer._label._container.title = options.title;
        layer._label._container.style.backgroundColor = 'rgba('+rgb.join(',')+ ',0.8)';
        layer._label._container.style.borderColor = 'rgba('+rgb.join(',')+ ',0.6)';
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

    self.restoreFullContext = function(map, context, kwargs) {
        if (!kwargs) kwargs = {};
        var filter = kwargs.filter,
            datatable = kwargs.datatable,
            objectsname = kwargs.objectsname;

        if (!context || typeof context != 'object') {
            // If not received from URL, load from LocalStorage
            context = self.__loadFullContext(kwargs);
        }
        if (!context) {
            console.warn("No context found.");
            map.fitBounds(map.options.maxBounds);
            return;  // No context, no restore.
        }

        if (context.mapsize) {
            // Override min-height style
            map._container.style.minHeight = '0';
            // Force map size
            if (context.mapsize.width && context.mapsize.width > 0)
                $('.map-panel').width(context.mapsize.width);
            if (context.mapsize.height && context.mapsize.height > 0)
                $('.map-panel').height(context.mapsize.height);
            map.invalidateSize();
        }

        self.restoreMapView(map, context, kwargs);

        if (filter && context.filter) {
            $(filter).deserialize(context.filter);
            $(filter).find('select').trigger("liszt:updated");
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

        if (context.print) {
            // Hide map head
            $('#maphead').hide();
            // Hide controls
            $('.leaflet-control').hide();   // Hide all
            $('.leaflet-control-scale').show(); // Show scale
            $(map._container).removeClass('leaflet-fade-anim');
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
                if (layer) {
                    if (layer instanceof L.Polyline) {
                        var n = layer.getLatLngs().length,
                            snaplist = new Array(n);
                        for (var i=0; i<n; i++) {
                            var marker = layer.editing._markers[i];
                            if (marker.snap && marker.snap.properties && marker.snap.properties.pk)
                                snaplist[i] = marker.snap.properties.pk;
                        }
                        serialized = {geom: L.Util.getWKT(layer),
                                      snap: snaplist};
                        serialized = JSON.stringify(serialized);
                    }
                    else {
                        serialized = L.Util.getWKT(layer);
                    }
                }
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
        $('#nbresults').text(infos.nb);
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
                    window.location = window.SETTINGS.server;
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
        infos = localStorage.getItem('list-search-results') || '{"nb": "?", "model": null}';
        infos = JSON.parse(infos);
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

        window.setTimeout(function () {
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
        }, 5000);  // Don't stress loading.
    },
});

MapEntity.history = new MapEntity.History();


function tr(s) { return s; }


MapEntity.TogglableFilter = L.Class.extend({
    includes: L.Mixin.Events,
    options: {},

    initialize: function () {
        this.button = '#filters-btn';

        this.fields = {};
        this.visible = false;
        this.popover = $('#filters-popover')
                          .popover({
                              placement: 'bottom',
                              html: true,
                              content: '',
                              title: 'Useless'
                          });
        this.hover = $('#filters-hover')
                          .popover({
                              placement: 'bottom',
                              html: true,
                              content: this.infos.bind(this),
                              title: tr("Current criteria")
                          });

        $(this.button).click(this.toggle.bind(this));
        $(this.button).hover(this.showinfo.bind(this));
        var self = this;
        $('#mainfilter').find('select,input').change(function (e) {
            self.setfield(this);
        });

        // Move all topology-filters to separate tab
        $('#mainfilter .topology-filter').parent('p')
                                         .detach().appendTo('#mainfilter > .right');

        // Use chosen for multiple values
        // Remove empty value (set with empty_label in Django for all choice fields)
        $('#mainfilter select[multiple] option:first-child').remove();
        $("form#mainfilter").bind("reset", function() {
            setTimeout(function() {
                $('form#mainfilter select[multiple]').trigger('liszt:updated');
            }, 1);
        });
        // Make sure filter-set class is added if a choice is selected.
        $('#mainfilter select[multiple]').chosen().on('change', function (e) {
            var $target = $(e.target),
                name = $target.attr('name'),
                $container = $('div#id_' + name + '_chzn > ul');
            if ($(e.target).find('option:selected').length > 0) {
                $container.addClass('filter-set');
            }
            else {
                $container.removeClass('filter-set');
            }
        });
    },

    tip: function () {
        return this.popover.data('popover').$tip;
    },

    htip: function () {
        return this.hover.data('popover').$tip;
    },

    __reposition: function (tip) {
        // Adjust position nicely along filter button
        var btnleft = $(this.button).position().left,
            btnwidth = $(this.button).width();
        tip.css('left', btnleft + btnwidth/2 - tip.width()/2);
    },

    showinfo: function () {
        // If popover is already visible, do not show hover
        if (this.visible)
            return;
        this.hover.popover('toggle');
        // Adjust popover width
        this.htip()
            .width(this.htip().find('.popover-title').outerWidth());
        this.__reposition(this.htip());
    },

    infos: function () {
        if (Object.keys(this.fields).length === 0)
            return "<p>" + tr("No filter") + "</p>";
        // We do not use handlebars just for this. If more to come, we will !
        var p = '<p><span class="filter-info">%name%</span>: %value%</p>';
        var i = '';
        for (var k in this.fields) {
            var f = this.fields[k];
            i += p.replace('%name%', f.label).replace('%value%', f.value);
        }
        return i;
    },

    toggle: function () {
        /* Show/Hide popover */
        if (this.visible) {
            // The whole $tip will be deleted, save the panel
            // and add it to the DOM so the dynamic filters still works.
            $('#filters-wrapper').append(
                this.tip().find('#filters-panel').detach()
            );
        }

        this.popover.popover('toggle');
        this.visible = !this.visible;

        if (this.visible) {
            this.tip()
              .empty()
              .append('<div class="arrow"/>')
              .append($('#filters-wrapper #filters-panel').detach());

            // Adjust popover width
            this.tip()
                .width(this.tip().find('#filters-panel form').outerWidth());

            this.__reposition(this.tip());
        }
    },

    setfield: function (field) {
        var label = $(field).data('label'),
            name = $(field).attr('name'),
            val = $(field).val(),
            set = val !== '' && val != [''];

        // Consider a value set if it is not the first option selected
        if ($(field).is('select[multiple]')) {
            set = val !== null;
        }
        else if ($(field).is('select')) {
            set = val != $(field).find('option').first().val();
        }

        // Displayed value
        var value = val;
        if (field.tagName == 'SELECT') {
            value = $(field).find("option:selected").text();
        }

        if (set) {
            this.fields[name] = {name: name, val:val, value:value, label:label};
        }
        else {
            delete this.fields[name];
        }

        if (set) {
            $(field).addClass('filter-set');
        }
        else {
            $(field).removeClass('filter-set');
        }
        return set;
    },

    setsubmit: function () {
        this.submitted = true;
        // Show fields as bold
        // Show button as active
        if (Object.keys(this.fields).length === 0) {
            $('#filters-btn').addClass('btn-info');
            $('#filters-btn').removeClass('btn-warning');
        }
        else {
            $('#filters-btn').removeClass('btn-info');
            $('#filters-btn').addClass('btn-warning');
        }
    }
});