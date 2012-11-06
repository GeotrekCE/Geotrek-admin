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
            var fields = $($('filter').serializeArray()).filter(function (){ return this.name != 'bbox'});
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

MapEntity.resetForm = function resetForm($form) {
    $form.find('input:text, input:password, input:file, select, textarea').val('');
    $form.find('input:radio, input:checkbox')
         .removeAttr('checked').removeAttr('selected');
}

MapEntity.showNumberSearchResults = function (nb) {
    if (arguments.length > 0) {
        localStorage.setItem('list-search-results', nb);
    }
    else {
        nb = localStorage.getItem('list-search-results') || '?';
    }
    $('#nbresults').text(nb);
}




MapEntity.MapListSync = L.Class.extend({
    includes: L.Mixin.Events,
    options: {
        filter: null,
        /* { form: $('#mainfilter'),
             submitbutton: $('#filter'),
             resetbutton: $('#reset'),
             bboxfield: $('#id_bbox'),
           }
        */
    },

    initialize: function (datatables, map, objectsLayer, options) {
        this.dt = datatables;
        this.map = map;
        this.layer = objectsLayer;
        L.Util.setOptions(this, options);
        
        this.selectorOnce = this.__initSelectorOnce(); // TODO: rename this and refactor
        this._dtcontainer = this.dt.fnSettings().nTableWrapper;
        
        this.dt.fnSettings().fnCreatedRow = this._onRowCreated.bind(this);
        this.layer.on('click', this._onObjectClick.bind(this));
        
        this._ignoreMap = false;
        this._loading = false;
        this._pk_list = null;
        this._initialBounds = null;
        if (this.map._loaded) {
            this._initialBounds = this.map.getBounds();
        }
        else {
            this.map.on('load', function () {
                this._initialBounds = this.map.getBounds();
                this._onMapViewChanged();
            }, this);
        }
        this.map.on('moveend', this._onMapViewChanged, this);
        
        if (this.options.filter) {
            this.options.filter.submitbutton.click(this._onFormSubmit.bind(this));
            this.options.filter.resetbutton.click(this._onFormReset.bind(this));
        }
    },

    _onMapViewChanged: function (e) {
        if (this._ignoreMap || !this.map._loaded)
            return;
        this._formSetBounds();
        this._reloadList();
    },

    _onFormSubmit: function (e) {
        this._formSetBounds();
        this._reloadList();
        this.layer.updateFromPks(this._pk_list);
    },

    _onFormReset: function (e) {
        this._ignoreMap = true;
        if (this._initialBounds) this.map.fitBounds(this._initialBounds);
        this._ignoreMap = false;
        
        this._formSetBounds();
        this._reloadList();
        this.layer.updateFromPks(this._pk_list);
    },

    _onObjectClick: function (e) {
        var self = this;
        var search_pk = e.layer.properties.pk;
        JQDataTable.goToPage(this.dt, 
            function pk_equals(row) {
                return row[0] === search_pk;
            }, function($row) {
                self.selectorOnce.select(search_pk, $row);
            }
        );
    },

    _onRowCreated: function(nRow, aData, iDataIndex ) {
        var pk = aData[0];
        $(nRow).hover(
            function(){
                this.layer.highlight(pk);
            },
            function(){
                this.layer.highlight(pk, false);
            }
        );

        // select from row
        var self = this;
        $(nRow).click(function() {
            self.selectorOnce.select(pk, $(nRow));
        });
        $(nRow).dblclick(function() {
            self.layer.jumpTo(pk);
        });
    },

    _reloadList: function () {
        if (this._loading)
            return;
        this._loading = true;
        this._pk_list = [];
        var spinner = new Spinner().spin(this._dtcontainer);
        
        // on JSON load, return the json used by dataTable
        // Update also the map given the layer's pk
        var self = this;
        var extract_data_and_pks = function(data, type, callback_args) {
            callback_args.map_obj_pk = data.map_obj_pk;
            return data.aaData;
        };
        var on_data_loaded = function (oSettings, callback_args) {
            self._loading = false;
            self._pk_list = callback_args.map_obj_pk;
            self.fire('reloaded', {
                nbrecords: self.dt.fnSettings().fnRecordsTotal(),
            });
            spinner.stop();
        };
        
        var url = this.options.url;
        if (this.options.filter) {
            url = this.options.filter.form.attr("action") + '?' + this.options.filter.form.serialize();
        }
        console.log(url);
        this.dt.fnReloadAjax(url, extract_data_and_pks, on_data_loaded);
        return false;
    },

    _formSetBounds: function () {
        if (!this.options.filter)
            return;
        
        if (!this.map._loaded) {
            console.warn("Map view not set, cannot get bounds.");
            return;
        }
        var bounds = this.map.getBounds(),
            rect = new L.Rectangle([bounds._northEast, bounds._southWest]);
        this.options.filter.bboxfield.val(L.Util.getWKT(rect));
    },



    __initSelectorOnce: function () {
        /**
         * This code was moved from entity list main page. A massive simplification
         * is required.
         */
        var self = this;
        var selectorOnce = (function() {
                var current = { 'pk': null, 'row': null };

                function toggleSelectRow($prevRow, $nextRow) {
                    function nextRowAnim() {
                        if ($nextRow) {
                            $nextRow.hide('fast')
                                    .show('fast', function() { $nextRow.addClass('selected-row'); });
                        }
                    }

                    if ($prevRow) {
                        $prevRow.hide('fast', function() { $prevRow.removeClass('selected-row'); })
                                .show('fast', nextRowAnim);
                    } else {
                        nextRowAnim();
                    }
                }

                function toggleSelectObject(pk, on) {
                    on = on === undefined ? true : on;
                    self.layer.select(pk, on);
                };

                return {
                    'select': function(pk, row) {
                        // Click on already selected => unselect
                        if (pk == current.pk) {
                            pk = null, row = null;
                        }

                        var prev = current;
                        current = {'pk': pk, 'row': row}

                        toggleSelectRow(prev.row, row);

                        if (prev.pk && prev.row) {
                            toggleSelectObject(prev.pk, false);
                        }
                        if (row && pk) {
                            toggleSelectObject(pk, true);
                        }
                    }
                };
            })();
        return selectorOnce;
    }
});
