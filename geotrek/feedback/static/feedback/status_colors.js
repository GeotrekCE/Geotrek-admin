L.MapListSynchro = L.Class.extend({
    includes: L.Mixin.Events,
    options: {
        filter: null,
    },

    initialize: function (datatables, map, layerGroup, options) {
        this.dt = datatables;
        this.map = map;
        //this.layer = objectsLayer;
        L.Util.setOptions(this, options);

        this.selectorOnce = this.__initSelectorOnce(); // TODO: rename this and refactor
        self = this;
        layerGroup.eachLayer(function (layer) {
            layer.on('mouseintent', self._onObjectOver.bind(this));
        });
        this._loading = false;
        this.map.on('moveend', this._onMapViewChanged, this);

        if (this.options.filter) {
            this.options.filter.submitbutton.click(this._onFormSubmit.bind(this));
            this.options.filter.resetbutton.click(this._onFormReset.bind(this));
        }
        $(this.dt.settings().oInstance).on('filter', this._onListFilter.bind(this));
    },

    _updateSeveralLayerFomPks: function (pks) {
        console.log("updating")
        for (var i = 0; i < window.objectsLayers.length; i++) {
            var self = window.objectsLayers[i],
                new_objects = {},
                already_added_layer,
                to_add_layer;

            // Gather all layer to see in new objects
            // Remove them from _current_objects if they are already shown
            // This way _current_objects will only contain layer to be removed
            $.each(data.pk_list, function (idx, to_add_pk) {
                already_added_layer = self._current_objects[to_add_pk];
                if (already_added_layer) {
                    new_objects[to_add_pk] = already_added_layer;
                    delete self._current_objects[to_add_pk];
                } else {
                    to_add_layer = new_objects[to_add_pk] = self._objects[to_add_pk];
                    // list can be ready before map, on first load
                    if (to_add_layer) self.addLayer(to_add_layer);
                }
            });

            // Remove all remaining layers
            $.each(self._current_objects, function (pk, layer) {
                self.removeLayer(layer);
            });

            self._current_objects = new_objects;
        }
    },

    _onListFilter: function () {
        var filterTxt = $(".dataTables_filter input[type='text']").val();
        var results = this.dt.fnGetColumnData(0);
        // this.fire('reloaded', {
        //     nbrecords: results.length,
        // });
        this._updateSeveralLayerFomPks(results)
        // layerGroup.eachLayer(function (layer) {
        //     console.log("11")
        //     //layer.updateFromPks(results);
        // });
    },

    _onMapViewChanged: function (e) {
        if (!this.map._loaded) {
            // leaflet bug, fire again !
            // fixed in unstable version : https://github.com/CloudMade/Leaflet/commit/fbf91fef546125bd4950937fa04ad1bf0f5dc955
            setTimeout(L.Util.bind(function () { this.map.fire(r); }, this), 20);
            return;
        }
        this._formSetBounds();
        //console.log("fom map view changed")
        this._reloadList();
    },

    _onFormSubmit: function (e) {
        this._formSetBounds();
        //console.log("fom submit")
        this._reloadList(true);
    },

    _onFormReset: function (e) {
        this._formClear($(this.options.filter.form)); // clear all fields
        //console.log("fom reset")
        this._reloadList();
        this._formSetBounds(); // re-fill current bbox
    },

    _onObjectOver: function (e) {
        var self = this;
        var search_pk = e.layer.properties.pk;
    },

    _onRowCreated: function (nRow, aData, iDataIndex) {
        var self = this;
        var pk = aData[0];
        $(nRow).hover(
            function () {
                self.layer.highlight(pk);
            },
            function () {
                self.layer.highlight(pk, false);
            }
        );

        // select from row
        $(nRow).click(function () {
            self.selectorOnce.select(pk, $(nRow));
        });
        $(nRow).dblclick(function () {
            self.layer.jumpTo(pk);
        });
    },

    _reloadList: function (refreshLayer) {
        var formData = new FormData(document.querySelector('#mainfilter'));
        var filter = false;

        for (var value of Array.from(formData)) {
            if (value[0] !== 'bbox') {
                if (value[1] !== '') {
                    filter = true;
                }
            }
        }
        if (filter) {
            $('#filters-btn').removeClass('btn-info');
            $('#filters-btn').addClass('btn-warning');
        }
        else {
            $('#filters-btn').removeClass('btn-warning');
            $('#filters-btn').addClass('btn-info');
        }

        console.log("ahax")
        this.dt.ajax.url($('#mainfilter').attr('action') + '?' + $('#mainfilter').serialize()).load();


        if (this._loading)
            return;
        this._loading = true;

        var spinner = new Spinner().spin(this._dtcontainer);

        // on JSON load, return the json used by dataTable
        // Update also the map given the layer's pk
        var self = this;
        var extract_data_and_pks = function (data, type, callback_args) {

            callback_args.map_obj_pk = data.map_obj_pk;
            return data.aaData;
        };
        var on_data_loaded = function (oSettings, callback_args) {
            var nbrecords = self.dt.fnSettings().fnRecordsTotal();
            var nbonmap = Object.keys(layerGroup.getLayers()).length;

            // We update the layer objects, only if forced or
            // if results has more objects than currently shown
            // (i.e. it's a trick to refresh only on zoom out
            //  cf. bug https://github.com/makinacorpus/Geotrek/issues/435)
            if (refreshLayer || (nbrecords > nbonmap)) {
                var updateLayerObjects = function (layer) {
                    console.log("reresh")
                    this._updateSeveralLayerFomPks(callback_args.map_obj_pk)
                    //layer.updateFromPks(callback_args.map_obj_pk);
                    self._onListFilter();
                };
                layerGroup.eachLayer(function (layer) {
                    if (layer.loading) {
                        //console.log("1")
                        // Layer is not loaded yet, delay object filtering
                        layer.on('loaded', updateLayerObjects(layer));
                    }
                    else {
                        // Do it immediately, but end up drawing.
                        setTimeout(updateLayerObjects, 0);
                    }
                });
            }
            self.fire('reloaded', {
                nbrecords: nbrecords,
            });

            spinner.stop();
            self._loading = false;  // loading done.
        };

        // get filtered pks
        $.get($('#mainfilter').attr('action').replace('.datatables', '/filter_infos.json'),
            $('#mainfilter').serialize(),
            function (data) {
                //console.log("mouoais?")
                $('#nbresults').text(data.count);
                // layerGroup.eachLayer(function (layer) {
                //     console.log("2")
                //     layer.updateFromPks(data.pk_list);
                // });
                //START OF COPIED
                for (var i = 0; i < window.objectsLayers.length; i++) {
                    var self = window.objectsLayers[i],
                        new_objects = {},
                        already_added_layer,
                        to_add_layer;

                    // Gather all layer to see in new objects
                    // Remove them from _current_objects if they are already shown
                    // This way _current_objects will only contain layer to be removed
                    $.each(data.pk_list, function (idx, to_add_pk) {
                        already_added_layer = self._current_objects[to_add_pk];
                        if (already_added_layer) {
                            new_objects[to_add_pk] = already_added_layer;
                            delete self._current_objects[to_add_pk];
                        } else {
                            to_add_layer = new_objects[to_add_pk] = self._objects[to_add_pk];
                            // list can be ready before map, on first load
                            if (to_add_layer) self.addLayer(to_add_layer);
                        }
                    });

                    // Remove all remaining layers
                    $.each(self._current_objects, function (pk, layer) {
                        self.removeLayer(layer);
                    });

                    self._current_objects = new_objects;
                }
                spinner.stop();
                self._loading = false;  // loading done.
            }.bind(this));

        var url = this.options.url;
        if (this.options.filter) {
            url = this.options.filter.form.attr("action") + '?' + this.options.filter.form.serialize();
        }
        //this.dt.fnReloadAjax(url, extract_data_and_pks, on_data_loaded);
        return false;
    },

    _formSetBounds: function () {
        if (!this.options.filter)
            return;

        if (!this.map._loaded) {
            console.warn("Map view not set, cannot get bounds.");
            return;
        }
        var bounds = this.map.getBounds();
        // get map bound coordinates, keep them in max real values
        var min_lat = Math.max(bounds._southWest.lat, -90);
        var max_lat = Math.min(bounds._northEast.lat, 90);
        var min_lon = Math.max(bounds._southWest.lng, -180);
        var max_lon = Math.min(bounds._northEast.lng, 180);

        var bounds = this.map.getBounds(),
            rect = new L.Rectangle([bounds._northEast, bounds._southWest]);
        this.options.filter.bboxfield.val(L.Util.getWKT(rect));
        //this.options.filter.bboxfield.val(`${min_lon},${min_lat},${max_lon},${max_lat}`);
    },

    _formClear: function ($form) {
        $form.find('input:text, input:password, input:file, select, textarea').val('').trigger('change');
        $form.find('input:radio, input:checkbox, select option')
            .removeAttr('checked').removeAttr('selected');
        $form.find('select').val('').trigger("chosen:updated");
    },

    __initSelectorOnce: function () {
        /**
         * This code was moved from entity list main page. A massive simplification
         * is required.
         */
        var self = this;
        var selectorOnce = (function () {
            var current = { 'pk': null, 'row': null };

            function toggleSelectRow($prevRow, $nextRow) {
                function nextRowAnim() {
                    if ($nextRow) {
                        $nextRow.hide('fast')
                            .show('fast', function () { $nextRow.addClass('success'); });
                    }
                }

                if ($prevRow) {
                    $prevRow.hide('fast', function () { $prevRow.removeClass('success'); })
                        .show('fast', nextRowAnim);
                } else {
                    nextRowAnim();
                }
            }

            function toggleSelectObject(pk, on) {
                on = on === undefined ? true : on;
                layerGroup.eachLayer(function (layer) {
                    layer.select(pk, on);
                });
            }

            return {
                'select': function (pk, row) {
                    // Click on already selected => unselect
                    if (pk == current.pk) {
                        pk = null, row = null;
                    }

                    var prev = current;
                    current = { 'pk': pk, 'row': row };

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


function getUrl(properties, layer) {
    return window.SETTINGS.urls.detail.replace(new RegExp('modelname', 'g'), properties.model.split(".")[1])
        .replace('0', properties.pk);
}

function bindHover() {
    // Maintain hovering over table hilights objects in map
    MapEntity.mainDatatable.rows().eq(0).each(function (index) {
        var row = MapEntity.mainDatatable.row(index);
        // Unbind MapEntity hover
        $(row.node()).unbind('mouseenter mouseleave');
        // Re-bind to highlight no matter which layer the object is in
        $(row.node()).hover(
            function () {
                window.objectsLayers.forEach(layer => {
                    layer.highlight(row.data().id);
                });
            },
            function () {
                window.objectsLayers.forEach(layer => {
                    layer.highlight(row.data().id, false);
                });
            }
        );
    });
}


function ChangeColors(e, data) {
    if (data.modelname != 'report')
        return;
    var map = data.map;

    // Create a group of layers (one layer = one color)
    var objectsLayers = [];

    // For each report status
    var status_ids_and_colors = JSON.parse($('#status_ids_and_colors').text());
    for (var status in status_ids_and_colors) {
        status_id = status_ids_and_colors[status]["id"]
        status_color = status_ids_and_colors[status]["color"]
        // Use this status' color...
        L.Util.extend(
            window.SETTINGS.map.styles["report-" + status_id] = { 'weight': 5, 'color': status_color, 'opacity': 0.9, fillOpacity: 0.9 },
        );
        // ... in creating layer with reports that have this status
        var layer = new L.ObjectsLayer(null, {
            modelname: "report",
            objectUrl: getUrl,
            style: { color: status_color },
            onEachFeature: function (geojson, layer) {
                if (geojson.properties.name) layer.bindLabel(geojson.properties.name);
            }
        });
        // Load layer and save to group
        layer.load("/api/report/report.geojson?_status_id=" + status_id)
        objectsLayers.push(layer);
    }
    // Create layer group and add to map
    layerGroup = L.layerGroup(objectsLayers)
    map.addLayer(layerGroup)
    // Sync layer to map to preserve classic layer functionnalities
    var dt = MapEntity.mainDatatable;
    var mapsync = new L.MapListSynchro(dt,
        map,
        layerGroup, {
        filter: {
            form: $('#mainfilter'),
            submitbutton: $('#filter'),
            resetbutton: $('#reset'),
            bboxfield: $('#id_bbox'),
        }
    });
    // Save to window to retrieve later
    window.objectsLayers = objectsLayers;

    // Listen to some events to maintain map functionalities (dirty...)
    // When page is first loaded, bind hovering and remove original data layer 
    objectsLayers[objectsLayers.length - 1].addEventListener("loaded", function () {
        map.removeLayer(window.objectsLayer);
        bindHover()
    });
    // Re-bind hovering everytime datatable content is changed
    $('#objects-list').on('draw.dt', bindHover);
}

function ChangeColor(e, data) {
    if (data.modelname != 'report')
        return;
    var map = data.map;
    map.eachLayer(function (layer) {
        if (layer.options['modelname'] === "report") {
            layer.setStyle({ color: $("#report_color").text() })
        }
    }
    )
}

function InitReportStatusLegend(e, data) {
    if (data.modelname != 'report')
        return;
    var map = data.map;

    var legend = L.control({ position: 'bottomleft' });
    legend.onAdd = function (map) {

        var div = L.DomUtil.create('div', 'legend-statuses');
        header = ['<span style="text-align: center;display: block;"><strong>' + tr("Statuses") + '</strong></span>']
        inner = []
        // For each report status
        var status_ids_and_colors = JSON.parse($('#status_ids_and_colors').text());
        for (var status in status_ids_and_colors) {
            status_label = status_ids_and_colors[status]["label"]
            status_color = status_ids_and_colors[status]["color"]
            status_id = status_ids_and_colors[status]["identifier"]
            div.innerHTML +=
                inner.push(
                    '<i class="legend-circle ' + status_id + '" style="background:' + status_color + '"></i> ' + status_label
                );
        }
        div.innerHTML = header
        div.innerHTML += inner.join('<br>');
        return div;
    };
    legend.addTo(map);

    $(".legend-statuses")[0].style.display = 'none'; // init as hidden, use selector in controls overlay to display

    var LegendLayer = L.Class.extend({
        onAdd: function (map) {
            $(".legend-statuses").toggle();
        },
        onRemove: function (map) {
            $(".legend-statuses").toggle();
        },
    });
    control = new LegendLayer()
    map.layerscontrol.addOverlay(control, tr("Legend"));
    map.addLayer(control); //init as visible
}

$(window).on('entity:map:detail', ChangeColor);
$(window).on('entity:map:list', ChangeColors);
$(window).on('entity:map:list', InitReportStatusLegend);