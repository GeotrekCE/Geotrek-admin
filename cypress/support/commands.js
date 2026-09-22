Cypress.Commands.add('login', (username = 'admin', password = 'admin') => {
  cy.session([username, password], () => {
    cy.visit('/login/')
    cy.get('input[name="username"]').type(username)
    cy.get('input[name="password"]').type(password)
    cy.get('form').submit()
    cy.url().should('not.include', '/login/')
  })
});

Cypress.Commands.add('mockTiles', () => {
    cy.intercept("https://*.openstreetmap.org/*/*/*.png", {fixture: "images/tile_osm.png"}).as("tiles_osm");
    cy.intercept("https://*.tile.opentopomap.org/*/*/*.png", {fixture: "images/tile_otm.png"}).as("tiles_otm");
    cy.intercept(/data\.geopf\.fr\/wmts\?LAYER=CADASTRALPARCELS/, {fixture: "images/tile_overlay.png"}).as("tiles_overlay");
});