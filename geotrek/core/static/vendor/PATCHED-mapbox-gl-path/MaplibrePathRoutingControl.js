import MapboxPathControl from "./PATCHED-mapbox-gl-path.js";

class MaplibrePathRoutingControl {
    /**
     * Constructeur de la classe MaplibrePathRoutingControl.
     * @param options {Object} - Options de configuration pour le contrôle de routage.
     */
    constructor(options = {}) {
        this.options = { ...options };
        this._map = null;
        this._container = null;
    }

    /**
     * Méthode appelée lors de l'ajout du contrôle à la carte.
     * @param map {maplibregl.Map} - L'instance de la carte Maplibre.
     * @returns {HTMLElement} - Le conteneur du contrôle.
     */
    onAdd(map) {
        this._map = map;
        // this._initDragAndDrop(map);
        return this._initContainer(map);
    }

    async getRoute(coordinates) {
        return fetch(
            `https://router.project-osrm.org/route/v1/driving/${coordinates.join(
            ";"
            )}?geometries=geojson`,
            {
                method: "GET",
                headers: { "Content-Type": "application/json" },
            }
        )
        .then((response) => response.json())
        .then((data) =>
        data.code === "Ok"
            ? {
                coordinates: data.routes[0].geometry.coordinates,
                waypoints: {
                    departure: data.waypoints[0].location,
                    arrival: data.waypoints[1].location,
                },
            }
            : undefined
        );
    }

    /**
     * Initialise le conteneur principal du contrôle de routage.
     * @param map {maplibregl.Map} - L'instance de la carte Maplibre.
     * @returns {HTMLElement} - Retourne le conteneur principal du contrôle.
     * @private
     */
    _initContainer(map) {
        // Création du conteneur principal
        this._container = document.createElement('div');
        // TODO: check that the css works:
        this._container.className = 'maplibregl-ctrl maplibregl-ctrl-group maplibregl-routing';

        // Création du bouton pour charger un fichier
        const button = document.createElement('button');
        button.setAttribute('type', 'button');
        button.setAttribute('title', gettext('Route on the path network'));
        button.className = 'maplibregl-ctrl-icon maplibregl-routing';

        const img = document.createElement('img');
        img.src = '/static/core/images/linetopology-control.png';
        img.alt = 'Route';
        img.style.width = '25px';
        img.style.height = '25px';
        img.style.padding = '2px';
        button.appendChild(img);
        this._container.appendChild(button);

        // Add mapbox-gl-path control
        const mapboxPathControl = new MapboxPathControl({
            translate: (text) => {
                const locales = { // TODO
                    "gl-pathControl.createPoint": "Create point",
                    "gl-pathControl.createIntermediatePoint": "Create intermediate point",
                    "gl-pathControl.deletePoint": "Delete point",
                    "gl-pathControl.loopPoint": "Round trip",
                    "gl-pathControl.oneWayPoint": "One way"
                }
                return locales[text]
            },
            directionsThemes: [
                {
                    id: 1,
                    name: 'Tracé sur tronçons',
                    selected: true,
                    getPathByCoordinates: this.getRoute,
                }
            ],
            layersCustomisation: {
                pointLayerList: [
                  // {
                  //   // First Point layer to display the "glow"
                  //   paint: {
                  //     "circle-radius": 14,
                  //     "circle-color": "#f7d4bc",
                  //   },
                  // },
                  {
                    // Second Point layer to display white circle
                    paint: {
                      "circle-radius": 10,
                      "circle-color": "#ffffff",
                      "circle-stroke-width": 2,
                      "circle-stroke-color": "#846b8a",
                    },
                  },
                  {
                    // Third Point layer to Alphabetical indexes
                    paint: {
                      "text-color": "#000",
                    },
                    type: "symbol",
                    layout: {
                      "text-size": 14,
                      "text-allow-overlap": true,
                    },
                  },
                ],
                lineLayerList: [
                  // {
                  //   // First LineString layer to display the "glow"
                  //   paint: { "line-width": 8, "line-color": "#f7d4bc" },
                  // },
                  {
                    // Second LineString layer to display the path
                    paint: { "line-width": 4, "line-color": "#846b8a" },
                  },
                  {
                    // Third LineString layer to the arrow icon
                    type: "symbol",
                    layout: {
                      //"icon-image": "arrow",
                      "icon-size": 0.6,
                      "symbol-placement": "line",
                      "icon-allow-overlap": true,
                    },
                  },
                ],
                phantomJunctionLineLayerList: [
                  {
                    paint: {
                      "line-width": 4,
                      "line-color": "#c98bb9",
                      "line-dasharray": [1, 1],
                    },
                  },
                ],
            }
        });

        button.onclick = () => {
            console.log("ROUTE!");
            map.addControl(mapboxPathControl, "top-left");
        }

        return this._container;
    }
}

export default MaplibrePathRoutingControl;