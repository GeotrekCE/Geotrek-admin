L.MapListSync = L.Class.extend({
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
        
        this.dt.fnSettings()['aoRowCreatedCallback'].push({
            fn: this._onRowCreated.bind(this),
            sName: 'user',
        });
        
        this.layer.on('click', this._onObjectClick.bind(this));
        
        this._loading = false;
        this.map.on('moveend', this._onMapViewChanged, this);
        
        if (this.options.filter) {
            this.options.filter.submitbutton.click(this._onFormSubmit.bind(this));
            this.options.filter.resetbutton.click(this._onFormReset.bind(this));
        }
        
        // Keep track of searched records, and refresh map.
        // Do not do it if event is received with no search 
        this._searched = false;
        var self = this;
        $(this.dt.fnSettings().oInstance).on('filter', function (e) {
            var filterTxt = $(".dataTables_filter input[type='text']").val();
            if ((self._searched && filterTxt == '') || 
                (!self._searched && filterTxt != '')) {
                self.layer.updateFromPks(self.dt.fnGetColumnData(0));
                self._searched = true;
            }
            else {
                self._searched = false;
            }
        });
    },

    _onMapViewChanged: function (e) {
        if (!this.map._loaded) {
            // leaflet bug, fire again !
            // fixed in unstable version : https://github.com/CloudMade/Leaflet/commit/fbf91fef546125bd4950937fa04ad1bf0f5dc955
            setTimeout(L.Util.bind(function() { this.map.fire('moveend'); }, this), 20);
            return;
        }
        this._formSetBounds();
        this._reloadList();
    },

    _onFormSubmit: function (e) {
        this._formSetBounds();
        this._reloadList(true);
    },

    _onFormReset: function (e) {
        this._formClear($(this.options.filter.form)); // clear all fields
        this._formSetBounds(); // re-fill current bbox
        this._reloadList();
        this.layer.updateFromPks(Object.keys(this.layer._objects));
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
        var self = this;
        var pk = aData[0];
        $(nRow).hover(
            function(){
                self.layer.highlight(pk);
            },
            function(){
                self.layer.highlight(pk, false);
            }
        );

        // select from row
        $(nRow).click(function() {
            self.selectorOnce.select(pk, $(nRow));
        });
        $(nRow).dblclick(function() {
            self.layer.jumpTo(pk);
        });
    },

    _reloadList: function (refreshLayer) {
        if (this._loading)
            return;
        this._loading = true;
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
            self.fire('reloaded', {
                nbrecords: self.dt.fnSettings().fnRecordsTotal(),
            });
            if(refreshLayer) self.layer.updateFromPks(callback_args.map_obj_pk);
            spinner.stop();
        };
        
        var url = this.options.url;
        if (this.options.filter) {
            url = this.options.filter.form.attr("action") + '?' + this.options.filter.form.serialize();
        }
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

    _formClear: function ($form) {
        $form.find('input:text, input:password, input:file, select, textarea').val('').trigger('change');
        $form.find('input:radio, input:checkbox')
             .removeAttr('checked').removeAttr('selected');
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
                                    .show('fast', function() { $nextRow.addClass('success'); });
                        }
                    }

                    if ($prevRow) {
                        $prevRow.hide('fast', function() { $prevRow.removeClass('success'); })
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
