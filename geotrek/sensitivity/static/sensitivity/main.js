$(window).on("entity:map", function (e, data) {
  if (data.modelname != "sensitivearea") {
    var map = data.map;

    // Show sensitivity layer in application maps
    var layer = new L.ObjectsLayer(null, {
      modelname: "sensitivearea",
      style: L.Util.extend(window.SETTINGS.map.styles["sensitivearea"] || {}, {
        clickable: false,
      }),
    });
    var url = window.SETTINGS.urls["sensitivearea_layer"];
    layer.load(url);
    map.layerscontrol.addOverlay(layer, tr("sensitivearea"), tr("Sensitivity"));
  }
});

const { createApp } = Vue;

const sensitiveAreaPublicDetailView = createApp({
  data() {
    return {
      message: "Hello Vue!",
      lang: "fr",
      sensitiveArea: null,
      url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      attribution:
        '&copy; <a target="_blank" href="http://osm.org/copyright">OpenStreetMap</a> contributors',
      zoom: 8,
      map: null,
      center: [47.31322, -1.319482],
      geojson: null,
      sportPractices: [],
      currentMonth: new Date().getMonth(),
      months: [
        "jan",
        "fév",
        "mar",
        "avr",
        "mai",
        "juin",
        "juil",
        "aout",
        "sep",
        "oct",
        "nov",
        "déc",
      ],
    };
  },
  computed: {
    properties() {
      return this.sensitiveArea ? this.sensitiveArea.properties : null;
    },
    typeZone() {
      return this.properties.species_id ? "Zone espèce" : "Zone réglementaire";
    },
    currentSensitivity() {
      return this.sensitiveArea.properties.period[this.currentMonth]
        ? "Sensible"
        : "Non sensible";
    },
  },
  methods: {
    emptyThumb(fileType) {
      return (
        "data:image/svg+xml;charset=utf-8," +
        encodeURIComponent(`
          <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
            <rect width="100" height="100" style="fill:#dddddd;" />
            <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" style="fill:#333;font-size:20px;font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'Liberation Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji';">
              ${fileType}
            </text>
          </svg>
          `)
      );
    },
    getSportPractices() {
      fetch(`/api/v2/sensitivearea_practice/?format=json`)
        .then((response) => response.json())
        .then((data) => (this.sportPractices = data.results));
    },
    getLang() {
      const lang = navigator.language.split("-")[0];
      const supportedLangs = ["en", "it", "fr"];
      this.lang = supportedLangs.includes(lang) ? lang : supportedLangs[0];
    },
    async getData() {
      const response = await fetch(
        `/api/v2/sensitivearea/${sensitiveAreaPk}/?format=geojson&period=any&language=${this.lang}`
      );
      this.sensitiveArea = await response.json();
    },
    addLayer() {
      const area = L.geoJson(this.sensitiveArea, {}).bindPopup(function (
        layer
      ) {
        return layer.feature.properties.name;
      });
      this.map.fitBounds(area.getBounds());
      this.map.setMaxBounds(area.getBounds());
      area.addTo(this.map);
    },
    initMap() {
      this.map = L.map("map").setView([51.505, -0.09], 13);
      this.map.maxZoom = 17;

      L.tileLayer("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", {
        attribution: `&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>,
              <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy;
              <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>`,
      }).addTo(this.map);
    },
  },
  mounted() {
    this.getLang();
    this.getSportPractices();
    this.getData()
      .then(() => this.initMap())
      .then(() => this.addLayer());
  },
});

sensitiveAreaPublicDetailView.config.compilerOptions.delimiters = ["[[", "]]"];
