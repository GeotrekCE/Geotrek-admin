var Geotrek = Geotrek || {};

L.Mixin.ActivableControl = {
    activable: function (activable) {
        /**
         * Allow to prevent user to activate the control.
         * (it is like setEnable(state), but ``enable`` word is used
         *  for handler already)
         */
        this._activable = activable;
        if (this._container) {
            if (activable)
                L.DomUtil.removeClass(this._container, 'control-disabled');
            else
                L.DomUtil.addClass(this._container, 'control-disabled');
        }

        this.handler.on('enabled', function (e) {
            L.DomUtil.addClass(this._container, 'enabled');
        }, this);
        this.handler.on('disabled', function (e) {
            L.DomUtil.removeClass(this._container, 'enabled');
        }, this);
    },

    setState: function (state) {
        if (state) {
            this.handler.enable.call(this.handler);
            this.handler.fire('enabled');
        }
        else {
            this.handler.disable.call(this.handler);
            this.handler.fire('disabled');
        }
    },

    toggle: function() {
        this._activable = !!this._activable;  // from undefined to false :)

        if (!this._activable)
            return;  // do nothing if not activable

        this.setState(!this.handler.enabled());
    },
};


L.Control.ExclusiveActivation = L.Class.extend({
    initialize: function () {
        this._controls = [];
    },

    add: function (control) {
        this._controls.push(control);
        var self = this;
        control.activable(true);
        control.handler.on('enabled', function (e) {
            // When this control is enabled, activate this one,
            // disable the others and prevent them to be activable.
            $.each(self._controls, function (i, c) {
                if (c != control) {
                    c.activable(false);
                }
            });
        }, this);

        control.handler.on('disabled', function (e) {
            // When this control is disabled, re-enable the others !
            // Careful, this will not take care of previous state :)
            $.each(self._controls, function (i, c) {
                c.activable(true);
            });
        }, this);
    },
});


L.Control.PointTopology = L.Control.extend({
    includes: L.Mixin.ActivableControl,

    statics: {
        TITLE: 'Point',
    },

    options: {
        position: 'topleft',
    },

    initialize: function (map, guidesLayer, field, options) {
        L.Control.prototype.initialize.call(this, options);
        this.handler = new L.Handler.PointTopology(map, guidesLayer, options);
        // Deactivate control once point is added
        this.handler.on('added', this.toggle, this);
    },

    onAdd: function (map) {
        this._container = L.DomUtil.create('div', 'leaflet-draw leaflet-control leaflet-bar leaflet-control-zoom');
        var link = L.DomUtil.create('a', 'leaflet-control-zoom-out pointtopology-control', this._container);
        link.href = '#';
        link.title = L.Control.PointTopology.TITLE;

        L.DomEvent.addListener(link, 'click', L.DomEvent.stopPropagation)
                  .addListener(link, 'click', L.DomEvent.preventDefault)
                  .addListener(link, 'click', this.toggle, this);
        return this._container;
    }
});


L.Handler.PointTopology = L.Draw.Marker.extend({
    initialize: function (map, guidesLayer, options) {
        L.Draw.Marker.prototype.initialize.call(this, map, options);
        this._topoMarker = null;
        this._guidesLayer = guidesLayer;

        map.on('draw:created', this._onDrawn, this);
    },

    reset: function() {
        if (this._topoMarker) {
            this._map.removeLayer(this._topoMarker);
        }
        this.fire('computed_topology', {topology: null});
    },

    restoreTopology: function (topo) {
        this._topoMarker = L.marker([topo.lat, topo.lng]);
        this._initMarker(this._topoMarker);
        if (topo.snap) {
            this._topoMarker.fire('move');  // snap to closest
        }
    },

    _onDrawn: function (e) {
        if (e.layerType === 'marker') {
            if (this._topoMarker !== null) {
                this._map.removeLayer(this._topoMarker);
            }

            this.fire('topo:created');
            this._topoMarker = L.marker(e.layer.getLatLng());
            this._initMarker(this._topoMarker);
        }
    },

    _initMarker: function (marker) {
        marker.addTo(this._map);
        L.DomUtil.addClass(marker._icon, 'marker-point');
        marker.editing = new L.Handler.MarkerSnap(this._map, marker);
        marker.editing.addGuideLayer(this._guidesLayer);
        marker.editing.enable();
        marker.on('move snap', function (e) {
            this.fire('computed_topology', {topology: marker});
        }, this);
        // Fire now : don't wait for move/snap (i.e. on click)
        this.fire('computed_topology', {topology: marker});
    },
});



L.Control.LineTopology = L.Control.extend({
    includes: L.Mixin.ActivableControl,

    statics: {
        TITLE: 'Route',
    },

    options: {
        position: 'topleft',
    },

    initialize: function (map, guidesLayer, field, options) {
        L.Control.prototype.initialize.call(this, options);
        this.handler = new L.Handler.MultiPath(map, guidesLayer, options);
    },

    onAdd: function (map) {
        this._container = L.DomUtil.create('div', 'leaflet-draw leaflet-control leaflet-bar leaflet-control-zoom');
        var link = L.DomUtil.create('a', 'leaflet-control-zoom-out linetopology-control', this._container);
        link.href = '#';
        link.title = L.Control.LineTopology.TITLE;

        L.DomEvent.addListener(link, 'click', L.DomEvent.stopPropagation)
                  .addListener(link, 'click', L.DomEvent.preventDefault)
                  .addListener(link, 'click', this.toggle, this);

        // Control is not activable until paths are loaded
        this.activable(false);

        return this._container;
    }
});


L.ActivableMarker = L.Marker.extend({
    initialize: function () {
        L.Marker.prototype.initialize.apply(this, arguments);
        this._activated = false;
        // Watch out if a callback is added and we are already in this state.
        // It won't be called !
        this.activate_cbs = [];
        this.deactivate_cbs = [];
    },

    activated: function() {
        return this._activated;
    },

    activate: function() {
        if (!this._activated) {
            for (var i = 0; i < this.activate_cbs.length; i++) {
                this.activate_cbs[i](this);
            }
            this._activated = true;
        }
    },

    deactivate: function() {
        if (this._activated) {
            for (var i = 0; i < this.deactivate_cbs.length; i++) {
                this.deactivate_cbs[i](this);
            }
            this._activated = false;
        }
    }
});


L.Handler.MultiPath = L.Handler.extend({
    includes: L.Mixin.Events,

    initialize: function (map, guidesLayer, options) {
        this.map = map;
        this._container = map._container;
        this._guidesLayer = guidesLayer;
        this._routeLayer = null
        this._routeTopology = []
        this._currentStepsNb = 0
        this._previousStepsNb = 0
        this.options = options;

        this.spinner = new Spinner()

        // Toast displayed when a marker was not dropped on a path:
        this._unsnappedMarkerToast = new bootstrap.Toast(
            document.getElementById("routing-unsnapped-marker-error-toast"),
            {delay: 5000}
        )
        // Toast displayed when there is no route due to a marker on an unreachable path:
        this._isolatedMarkerToast = new bootstrap.Toast(
            document.getElementById("routing-isolated-marker-error-toast"),
            {delay: 5000}
        )

        // Is the currently displayed route valid? i.e are all its markers linkable?
        this._routeIsValid = null

        // markers
        this.markersFactory = this.getMarkers();

        // Init a fresh state
        this.reset();

        this.idToLayer = function(id) {
            return guidesLayer.getLayer(id);
        };

        this.stepIndexToLayer = function(idx, layerArray) {
            if (!layerArray)
                return null
            for (var i = 0; i < layerArray.length; i++) {
                var layer = layerArray[i]
                if (layer.step_idx == idx)
                    return layer
            }
            return null;
        };

        this.layersOrderedByIdx = function() {
            if (!this._routeLayer)
                return []
            var layers = this._routeLayer.getLayers()
            var sortedLayers = layers.toSorted((first, second) => {
                return first.step_idx - second.step_idx
            })
            return sortedLayers
        }

        /*
         * Draggable via steps
         *
         * The following piece of code was also taken from formfield.js
         * It place is here, but needs refactoring to become elegant.
         */
        this.drawOnMouseMove = null;

        this.on('disabled', function() {
            this.drawOnMouseMove && this.map.off('mousemove', this.drawOnMouseMove);
        }, this);

        // Draggable marker initialisation and step creation
        var self = this;
        (function() {
            function dragstart(e) {
                var next_step_idx = self.draggable_marker.group_layer.step_idx + 1;
                self.addViaStep(self.draggable_marker, next_step_idx);
            }
            function dragend(e) {
                self.draggable_marker.off('dragstart', dragstart);
                self.draggable_marker.off('dragend', dragend);
                init();
            }
            function init() {
                self.draggable_marker = self.markersFactory.drag(new L.LatLng(0, 0), null, true);

                self.draggable_marker.on('dragstart', dragstart);
                self.draggable_marker.on('dragend', dragend);
                self.map.removeLayer(self.draggable_marker);
            }

            init();
        })();

        this.on('fetched_route', this.onFetchedRoute, this);
        this.on('invalid_route', this.onInvalidRoute, this);
    },

    // Reset the whole state
    reset: function() {
        var self = this;

        this.showPathGeom(null);

        // remove all markers from PointOnPolyline objects
        this.steps && $.each(this.steps, function(i, pop) {
            self.map.removeLayer(pop.marker);
        });

        // reset state
        this.steps = [];
        this.marker_source = this.marker_dest = null;
        this._routeTopology = []
        this._routeLayer = null
        this._currentStepsNb = 0
        this._previousStepsNb = 0
        this.fire('computed_topology', null);
    },

    // Activate/Deactivate existing steps and markers - mostly about (un)bindings listeners
    stepsToggleActivate: function(activate) {
        var cb;
        // /!\ Order in activation is important, first activate marker then pop
        // The marker.move listener must be set before the pop.move listener
        if (activate) {
            cb = function(pop) { pop.marker.activate(); pop.toggleActivate(true); }
        } else {
            cb = function(pop) { pop.marker.deactivate(); pop.toggleActivate(false); }
        }

        $(this.steps).each(function(i, pop) { pop && cb(pop); });
    },

    addHooks: function () {
        L.DomUtil.addClass(this._container, 'cursor-topo-start');

        this._guidesLayer.on('click', this._onClick, this);

        this.stepsToggleActivate(true);

        this.fire('enabled');
    },

    removeHooks: function() {
        L.DomUtil.removeClass(this._container, 'cursor-topo-start');
        L.DomUtil.removeClass(this._container, 'cursor-topo-end');
        this._guidesLayer.off('click', this._onClick, this);

        this.stepsToggleActivate(false);

        this.fire('disabled');
    },


    // On click on a layer with the graph
    _onClick: function(e) {
        var layer = e.layer
          , latlng = e.latlng

        var pop = this.addStartOrEndStep(layer, latlng)
        pop.events.fire('placed');
    },

    addStartOrEndStep: function(layer, latlng) {
        if (this.steps.length >= 2) return;

        var self = this;
        var next_step_idx = this.steps.length;
        var marker;

        if (next_step_idx == 0) {
            L.DomUtil.removeClass(this._container, 'cursor-topo-start');
            L.DomUtil.addClass(this._container, 'cursor-topo-end');
            marker = this.markersFactory.source(latlng);
            this.marker_source = marker;
        } else {
            L.DomUtil.removeClass(this._container, 'cursor-topo-start');
            L.DomUtil.removeClass(this._container, 'cursor-topo-end');
            marker = this.markersFactory.dest(latlng)
            this.marker_dest = marker;
        }

        var pop = self.createStep(marker, next_step_idx);
        pop.toggleActivate();
        self.forceMarkerToLayer(marker, layer);
        return pop
    },

    forceMarkerToLayer: function(marker, layer) {
        var closest = L.GeometryUtil.closest(this.map, layer, marker.getLatLng());
        marker.editing._updateSnap(marker, layer, closest);
    },

    createStep: function(marker, idx) {
        var self = this;

        var pop = new Geotrek.PointOnPolyline(marker);
        this.steps.splice(idx, 0, pop);  // Insert pop at position idx

        pop.events.on('placed', () => {

            if (!pop.isValid()) { // If the pop was not dropped on a path
                // Display an alert message
                this._unsnappedMarkerToast.show()

                if (pop.previousPosition) {
                    // If the pop was on a path before, set it to its previous position
                    pop.marker.setLatLng(pop.previousPosition.ll)
                    self.forceMarkerToLayer(pop.marker, pop.previousPosition.polyline);
                    if (!this._routeIsValid) {
                        // If the route is not valid, the marker must stay highlighted
                        L.DomUtil.removeClass(pop.marker._icon, 'marker-snapped');
                    }
                } else {
                    // If not, then it is a new pop: remove it
                    self.removeViaStep(pop)
                }
                return
            }
            if (this.steps.length > 1)
                this.enableLoadingMode()

            pop.previousPosition = {ll: pop.ll, polyline: pop.polyline}

            var currentStepIdx = self.getStepIdx(pop)

            // Create the array of new step indexes after the route is updated
            var newStepsIndexes = []
            if (currentStepIdx > 0)
                newStepsIndexes.push(currentStepIdx - 1)
            newStepsIndexes.push(currentStepIdx)
            if (currentStepIdx < self.steps.length - 1)
                newStepsIndexes.push(currentStepIdx + 1)

            // Create the array of step indexes before the route is updated
            var oldStepsIndexes
            if (this._currentStepsNb == this.steps.length)  // If a marker is being moved
                oldStepsIndexes = [...newStepsIndexes]
            else {  // If a marker is being added
                if (this._currentStepsNb == 1)  // If it's the destination
                    oldStepsIndexes = []
                else
                    oldStepsIndexes = newStepsIndexes.slice(0, -1)
            }

            this._previousStepsNb = this._currentStepsNb
            this._currentStepsNb = this.steps.length

            self.fetchRoute(oldStepsIndexes, newStepsIndexes, pop)
        });

        return pop;
    },

    // add an in between step
    addViaStep: function(marker, step_idx) {
        // A via step idx must be inserted between first and last...
        if (! (step_idx >= 1 && step_idx <= this.steps.length - 1)) {
            throw "StepIndexError";
        }

        var pop = this.createStep(marker, step_idx);

        var removeOnClick = () => this.removeViaStepFromRoute(pop)

        pop.marker.activate_cbs.push(() => marker.on('click', removeOnClick));
        pop.marker.deactivate_cbs.push(() => marker.off('click', removeOnClick));

        // marker is already activated, enable removeOnClick manually
        marker.on('click', removeOnClick)
        pop.toggleActivate();
        return pop
    },

    // Remove an existing step by clicking on it
    removeViaStepFromRoute: function(pop) {
        this.enableLoadingMode()
        var step_idx = this.getStepIdx(pop)
        this.removeViaStep(pop)
        this._previousStepsNb = this._currentStepsNb
        this._currentStepsNb = this.steps.length
        this.fetchRoute(
            [step_idx - 1, step_idx, step_idx + 1],
            [step_idx - 1, step_idx],
            pop
        );
    },

    // Remove a step from the steps list
    removeViaStep: function(pop) {
        var step_idx = this.getStepIdx(pop)
        this.steps.splice(step_idx, 1)
        this.map.removeLayer(pop.marker)
    },

    getStepIdx: function(step) {
        return this.steps.indexOf(step);
    },

    getStepIdxFromMarker: function(marker) {
        for (var i = 0; i < this.steps.length; i++) {
            if (this.steps[i].marker === marker)
                return i;
        }
        return -1;
    },

    getCookie: function(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },

    fetchRoute: function(oldStepsIndexes, newStepsIndexes, pop) {
        /*
            oldStepsIndexes: indexes of the steps for which to update the route
            newStepsIndexes: indexes of these steps after the route is updated
            pop (PointOnPolyline): step that is being added/modified/deleted
        */

        var stepsToRoute = []
        newStepsIndexes.forEach(idx => {
            stepsToRoute.push(this.steps[idx])
        })

        function canFetchRoute() {
            if (stepsToRoute.length < 2)
                return false;
            for (var i = 0; i < stepsToRoute.length; i++) {
                if (!stepsToRoute[i].isValid())
                    return false;
            }
            return true;
        }

        if (!canFetchRoute()) {
            this.disableLoadingMode()
            return
        }

        var sentSteps = []
        stepsToRoute.forEach((step) => {
            var sentStep = {
                path_id: step.polyline.properties.id,
                lat: step.ll.lat,
                lng: step.ll.lng,
            }
            sentSteps.push(sentStep)
        })

        fetch(window.SETTINGS.urls['route_geometry'], {
            method: 'POST',
            headers: {
                "X-CSRFToken": this.getCookie('csrftoken'),
                'Content-Type': 'application/json; charset=UTF-8',
            },
            body: JSON.stringify({
                steps: sentSteps,
            })
        })
        .then(response => {
            if (response.status == 200)
                return response.json()
            return Promise.reject(response)
        })
        .then(
            data => {  // Status code 200:
                if (data) {
                    var route = {
                        'geojson': data.geojson,
                        'serialized': data.serialized,
                        'oldStepsIndexes': oldStepsIndexes,
                        'newStepsIndexes': newStepsIndexes,
                    }
                    this.fire('fetched_route', route);
                }
            },
            // If the promise was rejected:
            response => {
                console.log("fetchRoute:", response)
                this.fire('invalid_route', pop)
            }
        )
        .catch(e => {
            console.log("fetchRoute", e)
            this.disableLoadingMode()
        })
    },

    enableLoadingMode: function () {
        // Prevent from modifying steps while the route is fetched
        this.spinner.spin(this._container);
        this.disableMarkers()
    },

    disableLoadingMode: function () {
        this.spinner.stop()
        // If the route is invalid, don't reenable the markers: some have
        // been disabled to guide the user through correcting the route.
        if (this._routeIsValid)
            this.enableMarkers()
    },

    restoreGeometry: function (serializedTopology) {
        var self = this;

        function pos2latlng(pos, layer) {
            var used_pos = pos;
            if (pos instanceof Array) {
                used_pos = pos[1];  // Default is second position (think of last path of topology)
                if (pos[0] == 0.0 && pos[1] != 1.0)
                    used_pos = pos[1];
                if (pos[0] == 1.0 && pos[1] != 0.0)
                    used_pos = pos[1];
                if (pos[0] != 1.0 && pos[1] == 0.0)
                    used_pos = pos[0];
                if (pos[0] != 0.0 && pos[1] == 1.0)
                    used_pos = pos[0];
            }
            var interpolated = L.GeometryUtil.interpolateOnLine(self.map, layer, used_pos);
            if (!interpolated) {
                throw ('Could not interpolate ' + used_pos + ' on layer ' + layer.properties.id);
            }
            return interpolated.latLng;
        };

        // Create and show the route geometry
        var restoredRouteLayer = L.featureGroup()
        serializedTopology.forEach((topology, idx) => {
            var groupLayer = this.buildGeometryFromTopology(topology);
            groupLayer.step_idx = idx
            restoredRouteLayer.addLayer(groupLayer)
        })
        this._routeLayer = restoredRouteLayer
        this.showPathGeom(restoredRouteLayer);

        this.setupNewRouteDragging(restoredRouteLayer)

        // Add the start marker
        var topology = serializedTopology[0]
        var pathLayer = this.idToLayer(topology.paths[0])
        var latlng = pos2latlng(topology.positions[0][0], pathLayer)
        var popStart = this.addStartOrEndStep(pathLayer, latlng)
        popStart.previousPosition = {ll: popStart.ll, polyline: popStart.polyline}

        // Add the end marker
        topology = serializedTopology[serializedTopology.length - 1]
        var lastPosIdx = topology.paths.length - 1
        pathLayer = this.idToLayer(topology.paths[lastPosIdx])
        latlng = pos2latlng(topology.positions[lastPosIdx][1], pathLayer)
        var popEnd = this.addStartOrEndStep(pathLayer, latlng)
        popEnd.previousPosition = {ll: popEnd.ll, polyline: popEnd.polyline}

        // Add the via markers: for each topology, use its first position,
        // except for the first topology (it would be the start marker)
        serializedTopology.forEach((topo, idx) => {
            if (idx == 0)
                return
            pathLayer = this.idToLayer(topo.paths[0])
            latlng = pos2latlng(topo.positions[0][0], pathLayer)
            var viaMarker = {
                layer: pathLayer,
                marker: self.markersFactory.drag(latlng, null, true)
            }
            var pop = self.addViaStep(viaMarker.marker, idx);
            self.forceMarkerToLayer(viaMarker.marker, viaMarker.layer);
            pop.previousPosition = {ll: pop.ll, polyline: pop.polyline}
        })

        // Set the state
        serializedTopology.forEach(topo => {
            this._routeTopology.push({
                positions: topo.positions,
                paths: topo.paths,
            })
        })
        this._currentStepsNb = this.steps.length
        this._previousStepsNb = this.steps.length
        this._routeIsValid = true
    },

    buildGeometryFromTopology: function (topology) {
        var latlngs = [];
        for (var i = 0; i < topology.paths.length; i++) {
            var path = topology.paths[i],
                positions = topology.positions[i],
                polyline = this.idToLayer(path);
            if (positions) {
                latlngs.push(L.GeometryUtil.extract(polyline._map, polyline, positions[0], positions[1]));
            }
            else {
                console.warn('Topology problem: ' + i + ' not in ' + JSON.stringify(topology.positions));
            }
        }
        return L.multiPolyline(latlngs);
    },

    showPathGeom: function (layer) {
        // This piece of code was moved from formfield.js, its place is here,
        // not around control instantiation. Of course this is not very elegant.
        var self = this;
        if (!this.markPath)
            this.markPath = (function() {
                var current_path_layer = null;
                return {
                    'updateGeom': function(new_path_layer) {
                        var prev_path_layer = current_path_layer;
                        current_path_layer = new_path_layer;

                        if (prev_path_layer) {
                            self.map.removeLayer(prev_path_layer);
                        }

                        if (new_path_layer) {
                            self.map.addLayer(new_path_layer);
                            new_path_layer.setStyle({'color': 'yellow', 'weight': 5, 'opacity': 0.8});
                            let stepIdx = 0;
                            new_path_layer.eachLayer(function (l) {
                                if (typeof l.setText == 'function') {
                                    l.setText('>  ', {repeat: true, attributes: {'fill': '#FF5E00'}});
                                    l.eachLayer((layer) => {
                                        layer._path.setAttribute('data-test', 'route-step-' + stepIdx);
                                    })
                                }
                                stepIdx++;
                            });
                        }
                    }
                }
            })();

            this.markPath.updateGeom(layer);
    },

    getMarkers: function() {
        var self = this;

        var map = this.map,
            guidesLayer = this._guidesLayer;

        // snapObserver and map are required to setup snappable markers
        // returns marker with an on('snap' possibility ?
        var dragging = false;
        function setDragging() { dragging = true; };
        function unsetDragging() { dragging = false; };
        function isDragging() { return dragging; };
        function activate(marker) {
            marker.dragging.enable();
            marker.editing.enable();
            marker.on('dragstart', setDragging);
            marker.on('dragend', unsetDragging);
        }
        function deactivate(marker) {
            marker.dragging.disable();
            marker.editing.disable();
            marker.off('dragstart', setDragging);
            marker.off('dragend', unsetDragging);
        }

        var markersFactory = {
            isDragging: isDragging,
            makeSnappable: function(marker) {
                marker.editing = new L.Handler.MarkerSnap(map, marker);

                marker.editing.addGuideLayer(guidesLayer);
                marker.editing.enable();

                marker.activate_cbs.push(activate);
                marker.deactivate_cbs.push(deactivate);
                marker.activate();
            },
            _generic: function (latlng, layer, classname, snappable) {
                var marker = new L.ActivableMarker(latlng, {draggable: true});
                map.addLayer(marker);
                marker.classname = classname;
                L.DomUtil.addClass(marker._icon, classname);

                if (snappable)
                    this.makeSnappable(marker);

                marker.dragging.enable();
                return marker;
            },
            source: function(latlng, layer) {
                return this._generic(latlng, layer, 'marker-source', true);
            },
            dest: function(latlng, layer) {
                return this._generic(latlng, layer, 'marker-target', true);
            },
            drag: function(latlng, layer, snappable) {
                return this._generic(latlng, layer, 'marker-drag', snappable);
            }
        };

        return markersFactory;
    },

    disableMarkers: function() {
        // Disable all markers on the map
        this.steps.forEach(step => {
            step.marker.deactivate();
        })
        // Prevent from creating new markers
        this.map.off('mousemove', this.drawOnMouseMove);
        this.map.removeLayer(this.draggable_marker);
    },

    enableMarkers: function() {
        // Enable all markers on the map
        this.steps.forEach(step => {
            step.marker.activate();
        })
        // Allow creating new markers again
        this.map.on('mousemove', this.drawOnMouseMove);
    },

    updateRouteLayers: function(geometries, oldStepsIndexes, newStepsIndexes) {
        var nbOldSteps = oldStepsIndexes.length
        var nbNewSteps = newStepsIndexes.length
        var previousRouteLayer = this._routeLayer.getLayers()

        // If a NEW via marker was unreachable, this invalid part of the path
        // was not displayed. So at this point, there is one more step, but
        // there isn't one more layer.
        var isNewMarkerBeingCorrected = this._routeIsValid == false && this._previousStepsNb > previousRouteLayer.length + 1

        // Remove out of date layers
        oldStepsIndexes.slice(0, -1).forEach((index, i) => {
            if (isNewMarkerBeingCorrected && i == nbOldSteps - 2)
                return
            var oldLayer = this.stepIndexToLayer(index, previousRouteLayer)
            if (oldLayer)
                this._routeLayer.removeLayer(oldLayer)
        })

        // Update the remaining layers' indexes
        this._routeLayer.eachLayer(function(subRouteLayer) {
            if (subRouteLayer.step_idx >= oldStepsIndexes.at(-1)) {
                // Adding a step: increment the next layers' indexes
                // Removing a step: decrement the next layers' indexes
                // Moving a step: no changes except...
                subRouteLayer.step_idx += (nbNewSteps - nbOldSteps)
            } else if (subRouteLayer.step_idx >= oldStepsIndexes.at(-1) - (isNewMarkerBeingCorrected && nbOldSteps == nbNewSteps)) {
                // ... if a new, unreachable marker is being moved and is now reachable, the
                // nb of layers increases by 1 and the next layers' indexes must be incremented
                subRouteLayer.step_idx += 1
            }
        })

        // Add the new layers
        newStepsIndexes.slice(0, -1).forEach((index, i) => {
            var newLayer = L.geoJson(geometries[i])
            newLayer.step_idx = index
            newLayer.setStyle({'color': 'yellow', 'weight': 5, 'opacity': 0.8});
            newLayer.eachLayer(function (l) {
                if (typeof l.setText == 'function') {
                    l.setText('>  ', {repeat: true, attributes: {'fill': '#FF5E00'}});
                }
            });
            this._routeLayer.addLayer(newLayer)
        })

        this._routeLayer.eachLayer(function (l) {
            if (typeof l.setText == 'function') {
                l.eachLayer((layer) => {
                    layer._path.setAttribute('data-test', 'route-step-' + l.step_idx);
                })
            }
        });
    },

    onFetchedRoute: function(data) {
        // Reset all the markers to 'snapped' appearance
        this.steps.forEach(step => {
            L.DomUtil.removeClass(step.marker._icon, 'marker-highlighted');
            L.DomUtil.removeClass(step.marker._icon, 'marker-disabled');
            L.DomUtil.addClass(step.marker._icon, 'marker-snapped');
            step.marker.activate();
        })
        oldStepsIndexes = data.oldStepsIndexes
        newStepsIndexes = data.newStepsIndexes

        if (!this._routeLayer) {
            this._routeLayer = L.featureGroup()
            this.map.addLayer(this._routeLayer);
            this.showPathGeom(this._routeLayer)
        }
        var previousRouteLayer = this._routeLayer.getLayers()
        this.updateRouteLayers(data.geojson.geometries, oldStepsIndexes, newStepsIndexes)

        var isNewMarkerBeingCorrected = this._routeIsValid == false && this._previousStepsNb > previousRouteLayer.length + 1

        // Store the new topology
        var nbSubToposToRemove = 0
        if (isNewMarkerBeingCorrected) {
            nbSubToposToRemove = 1
        } else if (oldStepsIndexes.length > 0) {
            // If it's not the first time displaying a layer
            nbSubToposToRemove = oldStepsIndexes.length - 1
        }
        var spliceArgs = [newStepsIndexes[0], nbSubToposToRemove].concat(data.serialized)
        this._routeTopology.splice.apply(this._routeTopology, spliceArgs)
        this.fire('computed_topology', {topology: this._routeTopology});

        this._routeIsValid = true
        this.setupNewRouteDragging(this._routeLayer)
        this.disableLoadingMode()
    },

    setupNewRouteDragging: function(routeLayer) {
        var self = this;

        // ## ONCE ##
        if (this.drawOnMouseMove) {
            this.map.off('mousemove', this.drawOnMouseMove);
        }

        var dragTimer = new Date();
        this.drawOnMouseMove = function(a) {
            var date = new Date();
            if ((date - dragTimer) < 25) {
                return;
            }
            if (self.markersFactory.isDragging()) {
                return;
            }

            dragTimer = date;

            for (var i = 0; i < self.steps.length; i++) {
                // Compare point rather than ll
                var marker_ll = self.steps[i].marker.getLatLng();
                var marker_p = self.map.latLngToLayerPoint(marker_ll);

                if (marker_p.distanceTo(a.layerPoint) < 10) {
                    self.map.removeLayer(self.draggable_marker);
                    return;
                }
            }

            var MIN_DIST = 30;

            var layerPoint = a.layerPoint
              , min_dist = Number.MAX_VALUE
              , closest_point = null
              , matching_group_layer = null;

            routeLayer && routeLayer.eachLayer(function(group_layer) {
                group_layer.eachLayer(function(layer) {
                    var p = layer.closestLayerPoint(layerPoint);
                    if (p && p.distance < min_dist && p.distance < MIN_DIST) {
                        min_dist = p.distance;
                        closest_point = p;
                        matching_group_layer = group_layer;
                    }
                });
            });

            if (closest_point) {
                self.draggable_marker.setLatLng(self.map.layerPointToLatLng(closest_point));
                self.draggable_marker.addTo(self.map);
                L.DomUtil.addClass(self.draggable_marker._icon, self.draggable_marker.classname);
                self.draggable_marker._removeShadow();
                self.draggable_marker.group_layer = matching_group_layer;
            } else {
                self.draggable_marker && self.map.removeLayer(self.draggable_marker);
            }
        };

        this.map.on('mousemove', this.drawOnMouseMove);
    },

    onInvalidRoute: function(pop) {
        this._routeIsValid = false
        this.fire('computed_topology', {topology: null});

        // Display an alert message
        this._isolatedMarkerToast.show()

        if (this.steps.length <= 2) {
            // If there are only two steps, both should be movable: enable them
            this.enableMarkers()
        } else {
            // Highlight the invalid marker and enable it
            L.DomUtil.removeClass(pop.marker._icon, 'marker-snapped');
            L.DomUtil.addClass(pop.marker._icon, 'marker-highlighted');
            pop.marker.activate()

            // Set the other markers to grey and disable them
            this.steps.forEach(step => {
                if (step._leaflet_id != pop._leaflet_id) {
                    L.DomUtil.removeClass(step.marker._icon, 'marker-snapped');
                    L.DomUtil.addClass(step.marker._icon, 'marker-disabled');
                    step.marker.deactivate();
                }
            })
            // Prevent from creating new via-steps
            this.map.off('mousemove', this.drawOnMouseMove);
            this.map.removeLayer(this.draggable_marker);
        }
        this.disableLoadingMode()
    }

});

// pol: point on polyline
Geotrek.PointOnPolyline = function (marker) {
    this.marker = marker;

    // If valid:
    this.ll = null;
    this.polyline = null;

    // To reset the pop to its previous valid position when not dropped on a path:
    this.previousPosition = null;

    this._activated = false;

    this.events = L.Util.extend({}, L.Mixin.Events);

    this.markerEvents = {
        'move': function onMove (e) {
            var marker = e.target;
            if (marker.snap) marker.fire('snap', {layer: marker.snap, latlng: marker.getLatLng()});
        },
        'snap': function onSnap(e) {
            this.ll = e.latlng;
            this.polyline = e.layer;
            this.events.fire('valid');
        },
        'unsnap': function onUnsnap(e) {
            this.ll = null;
            this.polyline = null;
            this.events.fire('invalid');
        },
        'dragend': function onDragEnd(e) {
            this.events.fire('placed');
        }
    };
};

Geotrek.PointOnPolyline.prototype.activated = function() {
    return this._activated;
};

Geotrek.PointOnPolyline.prototype.toggleActivate = function(activate) {
    activate = activate === undefined ? true : activate;

    if ((activate && this._activated) || (!activate && !this._activated))
        return;

    this._activated = activate;

    var method = activate ? 'on' : 'off';

    var marker = this.marker
      , markerEvents = this.markerEvents;

    marker[method]('move', markerEvents.move, this);
    marker[method]('snap', markerEvents.snap, this);
    marker[method]('unsnap', markerEvents.unsnap, this);
    marker[method]('dragend', markerEvents.dragend, this);
};

Geotrek.PointOnPolyline.prototype.isValid = function(graph) {
    return (this.ll && this.polyline);
};
