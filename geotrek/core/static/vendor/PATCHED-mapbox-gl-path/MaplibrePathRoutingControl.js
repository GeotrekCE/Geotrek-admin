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

        // // Création de l'input de type file
        // const fileInput = document.createElement('input');
        // fileInput.type = 'file';
        // fileInput.accept = '.gpx,.kml,.geojson';
        // fileInput.style.display = 'none';
        //
        // // Chargement du fichier lors d'un upload
        // fileInput.addEventListener("change", (e) => {
        //     if (e.target.files[0]) {
        //         this.load(e.target.files[0]);
        //     }
        // }, false);
        //
        // // Ajout de l'événement de clic pour charger le fichier
        // button.onclick = () => fileInput.click();
        // this._container.appendChild(fileInput);

        button.onclick = () => console.log("ROUTE!");

        return this._container;
    }
}

export default MaplibrePathRoutingControl;