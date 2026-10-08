Cypress.Commands.add('loginByCSRF', (username, password) => {
  cy.session(
    [username, password],
    () => {
      cy.request('/login/')
      .its('body')
      .then((body) => {
        // we can use Cypress.$ to parse the string body
        // thus enabling us to query into it easily
        const $html = Cypress.$(body);
        cy.request({
          method: 'POST',
          url: '/login/?next=/',
          failOnStatusCode: true, // dont fail so we can make assertions
          form: true, // we are submitting a regular form body
          body: {
            username,
            password,
            "csrfmiddlewaretoken": $html.find('input[name=csrfmiddlewaretoken]').val(), // insert this as part of form body
         }
        });
        cy.setCookie('django_language', 'en');
      });
    },
    {
      validate() {
        cy.request('/').its('status').should('eq', 200);
      },
    }
  );
});

Cypress.Commands.add('mockTiles', () => {
    cy.intercept("https://*.tile.opentopomap.org/*/*/*.png", {fixture: "images/tile.png"}).as("tiles");
    cy.intercept("https://*.tile.openstreetmap.org/*/*/*.png", {fixture: "images/tile.png"}).as("osmTiles");
    cy.intercept("http://*.tile.openstreetmap.org/*/*/*.png", {fixture: "images/tile.png"}).as("osmHttpTiles");
    cy.intercept(
      "https://data.geopf.fr/annexes/ressources/vectorTiles/styles/PLAN.IGN/standard.json",
      {
        body: {
          version: 8,
          glyphs: "https://data.geopf.fr/annexes/ressources/vectorTiles/fonts/{fontstack}/{range}.pbf",
          sources: {},
          layers: [],
        },
      }
    ).as("mapStyle");
    cy.intercept(
      "https://data.geopf.fr/annexes/ressources/vectorTiles/fonts/**",
      { body: new ArrayBuffer(0) }
    ).as("mapFonts");
    cy.intercept(
      "https://demotiles.maplibre.org/font/**",
      { body: new ArrayBuffer(0) }
    ).as("maplibreDemoFonts");
});


Cypress.Commands.add('setTinyMceContent', (tinyMceId, content) => {
  cy.window().then((win) => {
    const editor = win.tinymce.get(tinyMceId);
    editor.setContent(content);
  });
});

Cypress.Commands.add('getTinyMceContent', (tinyMceId, content) => {
  cy.window().then((win) => {
    const editor = win.tinymce.get(tinyMceId);
    return editor.getContent();
  });
});

const DEFAULT_TEST_VIEW = {
  center: [2.3628, 46.2833],
  zoom: 14,
};

Cypress.Commands.add('waitForMap', (mapSelector = '.maplibre-map', view = DEFAULT_TEST_VIEW) => {
  cy.get(mapSelector).find('.maplibregl-canvas').should('be.visible');
  cy.window().should((win) => {
    expect(win.maps).to.be.an('array').and.not.be.empty;
    const map = win.maps[0].getMap();
    expect(map).to.exist;
    expect(map.loaded()).to.be.true;
  });
  if (view) {
    cy.window().then((win) => {
      const map = win.maps[0].getMap();
      map.jumpTo({ center: view.center, zoom: view.zoom });
    });
  }
});

Cypress.Commands.add('waitForPathSnapLayer', (bbox = [[150, 150], [450, 250]]) => {
  cy.window().should((win) => {
    const map = win.maps[0].getMap();
    expect(map.getLayer('mapentity-snap-layer-path')).to.exist;
    expect(win.gm?.actionInstances?.helper__snapping).to.exist;
    const features = map.queryRenderedFeatures(bbox, {
      layers: ['mapentity-snap-layer-path'],
    });
    expect(features.length).to.be.greaterThan(0);
  });
});

Cypress.Commands.add('waitForPathRoutingLayer', (bbox = [[150, 150], [450, 250]]) => {
  cy.window().should((win) => {
    const map = win.maps[0].getMap();
    const pathLayer = win.pathLayerName || 'layer-path-lines';
    expect(map.getLayer(pathLayer)).to.exist;
    expect(map.getSource('mapbox-gl-path-source-point-and-line')).to.exist;
    const features = map.queryRenderedFeatures(bbox, {
      layers: [pathLayer],
    });
    expect(features.length).to.be.greaterThan(0);
  });
});

Cypress.Commands.add('drawGeomanLine', (mapSelector, points, fieldId = 'id_geom') => {
  const drawBtnSelector = `#${fieldId}_draw_line`;
  const canvasContainer = `${mapSelector} .maplibregl-canvas-container`;

  cy.get(drawBtnSelector).should('be.visible').click();
  cy.get(drawBtnSelector).should('have.class', 'active');

  points.forEach(([x, y]) => {
    cy.get(canvasContainer).trigger('mousemove', x, y, { force: true });
    cy.wait(50);
    cy.get(canvasContainer).click(x, y, { force: true });
    cy.wait(50);
  });

  // Click the last vertex marker element to finish the Geoman line
  cy.get(`${mapSelector} .maplibregl-marker`).last().click({ force: true });

  cy.get(`#${fieldId}`).should(($input) => {
    expect($input.val()).to.not.be.empty;
  });
});

Cypress.Commands.add('drawGeomanPoint', (mapSelector, [x, y], fieldId = 'id_geom') => {
  const drawBtnSelector = `#${fieldId}_draw_marker`;
  const canvasContainer = `${mapSelector} .maplibregl-canvas-container`;

  cy.get(drawBtnSelector).should('be.visible').click();
  cy.get(drawBtnSelector).should('have.class', 'active');

  // First mousemove populates external layer snapping coordinates (or clears them if off-path)
  cy.get(canvasContainer).trigger('mousemove', x, y, { force: true });
  cy.wait(50);
  // Second mousemove + click updates Geoman MarkerPointer (after 10ms throttle) and places the marker
  cy.get(canvasContainer).trigger('mousemove', x, y, { force: true });
  cy.wait(50);
  cy.get(canvasContainer).click(x, y, { force: true });

  cy.get(`#${fieldId}`).should(($input) => {
    expect($input.val()).to.not.be.empty;
  });
});

Cypress.Commands.add('submitEntityForm', () => {
  cy.get('#save_changes, #submit-id-save_changes').first().click();
});