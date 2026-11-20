describe('Verify path layer checkbox in topological edit forms', () => {
  beforeEach(() => {
    cy.loginByCSRF('admin', 'admin');
    cy.mockTiles();
  });

  it('checks the Paths checkbox on POI edit page', () => {
    cy.visit('/poi/edit/3/');
    cy.waitForMap('#id_geom_map');
    cy.get('#id_geom_map .layer-switcher-btn').click();
    cy.get('#id_geom_map .layer-switcher-menu').should('be.visible');
    cy.get('#id_geom_map .layer-switcher-menu label')
      .contains('Paths')
      .find('input[type="checkbox"]')
      .should('be.checked');
  });

  it('checks the Paths checkbox on Trek edit page', () => {
    cy.visit('/trek/edit/1/');
    cy.waitForMap('#id_topology_map');
    cy.get('#id_topology_map .layer-switcher-btn').click();
    cy.get('#id_topology_map .layer-switcher-menu').should('be.visible');
    cy.get('#id_topology_map .layer-switcher-menu label')
      .contains('Paths')
      .find('input[type="checkbox"]')
      .should('be.checked');
  });
});
