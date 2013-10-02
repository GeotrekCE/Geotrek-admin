L.FieldStore.TopologyStore = L.FieldStore.extend({

    _deserialize: function (value) {
        return value ? JSON.parse(value) : null;
    },

    _serialize: function (layer) {
        if (layer instanceof L.Marker) {
            var p = layer.getLatLng();
            serialized = {lat: p.lat, lng: p.lng};
            // In case the marker is snapped, serialize this information.
            if (layer.snap) {
                serialized['snap'] = layer.snap.properties.pk;
            }
        }
        else {
            serialized = layer;  // Returned by TopologyHelper
        }
        return JSON.stringify(serialized);
    }
});


MapEntity.GeometryField.TopologyField = MapEntity.GeometryField.extend({
    options: {
        field_store_class: L.FieldStore.TopologyStore,
    },

    includes: MapEntity.GeometryField.GeometryFieldPathMixin,

    initialize: function () {
        MapEntity.GeometryField.prototype.initialize.apply(this, arguments);
        this.options.modifiable = false; // Will disable leaflet.draw in leaflet.forms.js
        this._objectsLayer = null;
        this._pathsLayer = null;
        this._pointControl = null;
        this._multipathControl = null;
    },

    addTo: function (map) {
        MapEntity.GeometryField.prototype.addTo.call(this, map);
        this._initTopologyControl(map);
    },

    _initTopologyControl: function (map) {
        // This will make sure that we can't activate a control, while the
        // other is being used.
        var exclusive = new L.Control.ExclusiveActivation();

        if (this.options.is_point_topology) {
            this._pointControl = new L.Control.TopologyPoint(map,
                                                             this._pathsLayer,
                                                             this);
            map.addControl(this._pointControl);
            exclusive.add(this._pointControl);
            this._pointControl.handler.on('added', function (e) {
                this.save(e.marker);
            }, this);
        }

        if (this.options.is_line_topology) {
            this._multipathControl = new L.Control.Multipath(map,
                                                             this._pathsLayer,
                                                             this);
            map.addControl(this._multipathControl);
            exclusive.add(this._multipathControl);
            this._multipathControl.handler.on('computed_topology', function (e) {
                this.store.save(e.topology);
            }, this);
        }
    },

    buildObjectsLayer: function () {
        this._objectsLayer = MapEntity.GeometryField.prototype.buildObjectsLayer.call(this);
        this._pathsLayer = this.buildPathsLayer(this._objectsLayer);
        this._pathsLayer.on('loaded', this._loadTopologyGraph, this);
        return this._objectsLayer;
    },

    _loadTopologyGraph: function () {
        // Make sure paths stay above other layers
        this._pathsLayer.bringToFront();

        if (this._multipathControl === null) {
            // No need to load graph for point topologies
            this.load();
            return;
        }

        // Path layer is ready, load graph !
        this._pathsLayer.fire('data:loading');
        var url = window.SETTINGS.urls.path_graph + '?_u=' + (new Date().getTime());
        $.getJSON(url, this._onGraphLoaded.bind(this))
         .error(graphError.bind(this));

        function graphError(jqXHR, textStatus, errorThrown) {
            this._pathsLayer.fire('data:loaded');
            $(this._map._container).addClass('map-error');
            console.error("Could not load url '" + window.SETTINGS.url.path_graph + "': " + textStatus);
            console.error(errorThrown);
        }
    },

    _onGraphLoaded: function (graph) {
        // Load graph
        this._multipathControl.setGraph(graph);
        this.load();
        // Stop spinning !
        this._pathsLayer.fire('data:loaded');
    },

    load: function () {
        var topo = this.store.load();
        if (topo) {
            console.debug("Deserialize topology: " + topo);
            if (this._multipathControl && !topo.lat && !topo.lng) {
                this._multipathControl.handler.restoreTopology(topo);
            }
            if (this._pointControl && topo.lat && topo.lng) {
                this._pointControl.handler.restoreTopology(topo);
            }
        }
    }
});
