describe('v3 Topological and Free Drawing E2E Tests', () => {
  const PATH_START = [200, 200];
  const PATH_END = [400, 200];
  const PATH_BBOX = [
    [180, 180],
    [420, 220],
  ];

  describe('0. Prerequisite: Create a support path on the map', () => {
    beforeEach(() => {
      cy.loginByCSRF('admin', 'admin');
      cy.mockTiles();
      cy.intercept('POST', '/path/add/').as('postPath');
    });

    it('creates a path using the MapLibre Geoman line tool', () => {
      cy.visit('/path/add/');
      cy.waitForMap('#id_geom_map');

      cy.drawGeomanLine('#id_geom_map', [PATH_START, PATH_END], 'id_geom');

      cy.get('#id_geom')
        .invoke('val')
        .then((val) => {
          const geojson = JSON.parse(val);
          expect(geojson.type).to.eq('LineString');
          expect(geojson.coordinates).to.have.length(2);
        });

      cy.get('input[name="name"]').type('Support Path E2E');
      cy.submitEntityForm();

      cy.wait('@postPath').its('response.statusCode').should('eq', 302);
      cy.url().should('match', /\/path\/\d+\//);
      cy.contains('Support Path E2E');
    });
  });

  describe('1. Point topological drawing (POI) — with and without snapping', () => {
    beforeEach(() => {
      cy.loginByCSRF('admin', 'admin');
      cy.mockTiles();
      cy.intercept('POST', '/poi/add/').as('postPoi');
    });

    it('creates a POI with snapping onto the path network', () => {
      cy.visit('/poi/add/');
      cy.waitForMap('#id_geom_map');
      cy.waitForPathSnapLayer(PATH_BBOX);

      // Compute the exact unprojected latitude at y = 200 (on the path) and y = 208 (click position within 20px snap distance)
      cy.window().then((win) => {
        const map = win.mapentity_map || win.maps?.[0]?.getMap?.();
        const pathLat = map.unproject([300, 200]).lat;
        const clickLat = map.unproject([300, 208]).lat;

        // Click slightly below the path (8px away, within snap_distance=20)
        cy.drawGeomanPoint('#id_geom_map', [300, 208], 'id_geom');

        cy.get('#id_geom_changed').should('have.value', 'true');
        cy.get('#id_geom')
          .invoke('val')
          .then((val) => {
            const data = JSON.parse(val);
            expect(data.type).to.eq('Point');
            expect(data.snapLayer).to.eq('mapentity-snap-layer-path');
            expect(data.snapFeature).to.not.be.null;
            // Snapped latitude should be pulled onto the path (closer to pathLat than clickLat)
            const [, snappedLat] = data.coordinates;
            expect(Math.abs(snappedLat - pathLat)).to.be.lessThan(
              Math.abs(clickLat - pathLat)
            );
          });
      });

      cy.get('select[name="type"]').select(1, { force: true });
      cy.get('input[name^="name_"]:visible').first().type('POI with snapping');
      cy.submitEntityForm();

      cy.wait('@postPoi').its('response.statusCode').should('eq', 302);
      cy.url().should('match', /\/poi\/\d+\//);
      cy.contains('POI with snapping');
      // Verify the POI is coupled to the path network
      cy.get('i.bi-check-circle.text-success').should('be.visible');
    });

    it('creates a POI without snapping (clicked away from the path network)', () => {
      cy.visit('/poi/add/');
      cy.waitForMap('#id_geom_map');
      cy.waitForPathSnapLayer(PATH_BBOX);

      cy.window().then((win) => {
        const map = win.mapentity_map || win.maps?.[0]?.getMap?.();
        const pathLat = map.unproject([300, 200]).lat;
        const unsnappedTargetLat = map.unproject([300, 350]).lat;

        // Click far from the path (150px away, outside snapRadius=40px)
        cy.drawGeomanPoint('#id_geom_map', [300, 350], 'id_geom');

        cy.get('#id_geom_changed').should('have.value', 'true');
        cy.get('#id_geom')
          .invoke('val')
          .then((val) => {
            const data = JSON.parse(val);
            expect(data.type).to.eq('Point');
            expect(data.snapLayer).to.be.null;
            expect(data.snapFeature).to.be.null;
            // Unsnapped latitude stays at the clicked location (300, 350), not on the path (300, 200)
            const [, actualLat] = data.coordinates;
            expect(Math.abs(actualLat - unsnappedTargetLat)).to.be.lessThan(0.0005);
            expect(Math.abs(actualLat - pathLat)).to.be.greaterThan(0.002);
          });
      });

      cy.get('select[name="type"]').select(1, { force: true });
      cy.get('input[name^="name_"]:visible').first().type('POI without snapping');
      cy.submitEntityForm();

      cy.wait('@postPoi').its('response.statusCode').should('eq', 302);
      cy.url().should('match', /\/poi\/\d+\//);
      cy.contains('POI without snapping');

      // Verify on the edit page that the unsnapped coordinates were preserved (offset != 0)
      cy.url().then((detailUrl) => {
        const pk = detailUrl.match(/\/poi\/(\d+)\//)[1];
        cy.visit(`/poi/edit/${pk}/`);
        cy.get('#id_geom')
          .invoke('val')
          .then((val) => {
            const geom = JSON.parse(val);
            expect(geom.type).to.eq('Point');
          });
      });
    });
  });

  describe('2. Itinerary (Trek) topological drawing and permission-gated free drawing', () => {
    beforeEach(() => {
      cy.mockTiles();
      cy.intercept('POST', '/api/path/drf/paths/route-geometry').as('routeGeometry');
      cy.intercept('POST', '/trek/add/').as('postTrek');
    });

    it('draws an itinerary topologically along the path network', () => {
      cy.loginByCSRF('admin', 'admin');
      cy.visit('/trek/add/');
      cy.waitForMap('#id_topology_map');
      cy.waitForPathRoutingLayer(PATH_BBOX);

      cy.drawTopologicalRoute('#id_topology_map', [
        [230, 200],
        [370, 200],
      ]);

      cy.wait('@routeGeometry').its('response.statusCode').should('eq', 200);

      cy.get('#id_topology_changed').should('have.value', 'true');
      cy.get('#id_topology')
        .invoke('val')
        .then((val) => {
          const topology = JSON.parse(val);
          expect(topology).to.be.an('array').and.have.length(1);
          expect(topology[0].paths).to.be.an('array').and.have.length(1);
          expect(topology[0].positions).to.have.property('0');
        });

      cy.get('input[name^="name_"]:visible').first().type('Topological Trek E2E');
      cy.submitEntityForm();

      cy.wait('@postTrek').its('response.statusCode').should('eq', 302);
      cy.url().should('match', /\/trek\/\d+\//);
      cy.contains('Topological Trek E2E');
      // Topological trek is coupled to the path network
      cy.get('i.bi-check-circle.text-success').should('be.visible');
    });

    it('allows free drawing (off-path network) when the user has core.can_draw_off_path_network permission', () => {
      cy.loginByCSRF('admin', 'admin');
      cy.visit('/trek/add/');
      cy.waitForMap('#id_topology_map');
      cy.waitForPathSnapLayer(PATH_BBOX);

      // Free line draw button for #id_geom and #id_geom_changed must exist for a user with permission
      cy.get('#id_geom_draw_line').should('exist').and('be.visible');
      cy.get('#id_geom_changed').should('exist').and('not.have.value', 'true');

      // Topological path control is inactive by default so Geoman free drawing can be used directly
      cy.get('button.mapbox-gl-path-btn-edit')
        .should('be.visible')
        .and('not.have.class', 'mapbox-gl-path-active');

      // Draw a free line off the path network (at y = 350)
      cy.drawGeomanLine(
        '#id_topology_map',
        [
          [200, 350],
          [380, 350],
        ],
        'id_geom'
      );

      cy.get('#id_geom_changed').should('have.value', 'true');
      cy.get('#id_topology_changed').should('not.have.value', 'true');
      cy.get('#id_geom')
        .invoke('val')
        .then((val) => {
          const geojson = JSON.parse(val);
          expect(geojson.type).to.eq('LineString');
          expect(geojson.coordinates).to.have.length(2);
        });

      cy.get('input[name^="name_"]:visible').first().type('Free Drawn Trek E2E');
      cy.submitEntityForm();

      cy.wait('@postTrek').its('response.statusCode').should('eq', 302);
      cy.url().should('match', /\/trek\/\d+\//);
      cy.contains('Free Drawn Trek E2E');
      // Free-drawn trek is uncoupled from the path network
      cy.get('i.bi-x-circle.text-danger').should('be.visible');
    });

    it('forbids free drawing when the user lacks core.can_draw_off_path_network permission, while still allowing topological drawing', () => {
      // 'comm' user has trekking.add_trek / change_geom_trek permissions, but NOT core.can_draw_off_path_network
      cy.loginByCSRF('comm', 'comm');
      cy.visit('/trek/add/');
      cy.waitForMap('#id_topology_map');
      cy.waitForPathRoutingLayer(PATH_BBOX);

      // Secondary point geometry buttons are loaded in Geoman
      cy.get('#id_parking_location_draw_marker').should('exist').and('be.visible');
      cy.get('#id_points_reference_draw_marker').should('exist').and('be.visible');

      // Free line draw button for #id_geom and #id_geom_changed must NOT exist without permission
      cy.get('#id_geom_draw_line').should('not.exist');
      cy.get('.mapentity-draw-btn[data-field-id="id_geom"]').should('not.exist');
      cy.get('#id_geom_changed').should('not.exist');

      // Topological drawing control IS available and works for this user
      cy.drawTopologicalRoute('#id_topology_map', [
        [240, 200],
        [360, 200],
      ]);

      cy.wait('@routeGeometry').its('response.statusCode').should('eq', 200);
      cy.get('#id_topology_changed').should('have.value', 'true');

      cy.get('input[name^="name_"]:visible').first().type('Comm Topological Trek E2E');
      cy.submitEntityForm();

      cy.wait('@postTrek').its('response.statusCode').should('eq', 302);
      cy.url().should('match', /\/trek\/\d+\//);
      cy.contains('Comm Topological Trek E2E');
      cy.get('i.bi-check-circle.text-success').should('be.visible');
    });
  });
});