describe('Create trek', () => {
  beforeEach(() => {
      const username = 'admin'
      const password = 'admin'
      cy.request('/login/?next=/')
        .its('body')
        .then((body) => {
          // we can use Cypress.$ to parse the string body
          // thus enabling us to query into it easily
          const $html = Cypress.$(body)
          const csrf = $html.find('input[name=csrfmiddlewaretoken]').val()

          cy.loginByCSRF(csrf, username, password)
          .then((resp) => {
            expect(resp.status).to.eq(200)
          })
        })
  })

  it('Create path', () => {
    cy.visit('http://localhost:8000/trek/list')
    cy.get("a.btn-success[href='/trek/add/']").contains('Add a new trek').click()
    cy.get("a.linetopology-control").click()
    cy.get('.leaflet-map-pane')
      .click(380, 220)
      .click(450, 150);
    cy.get("input[name='name']").type('Trek number 1')
    cy.get("a[href='#name_fr']").click()
    cy.get("input[name='name']").type('Randonnée numéro 1')
    cy.get("input[id='id_review']").click()
    cy.get("input[id='id_is_park_centered']").click()
    cy.get("input[id='id_departure_en']").type('Departure')
    cy.get("a[href='#departure_fr']").click()
    cy.get("input[id='id_departure_fr']").type('Départ')
    cy.get("input[id='id_arrival_en']").type('Arrival')
    cy.get("a[href='#arrival_en']").click()
    cy.get("input[id='id_arrival_fr']").type('Arrivée')
    cy.get("input[id='id_duration']").type('100')
    cy.get("select[id='id_practice']").click()
    cy.get("option[value='2']").contains("Cycling").click()
    cy.get("select[id='id_difficulty']").click()
    cy.get("option[value='5']").contains("Very hard").click()
    cy.get("select[id='id_route']").click()
    cy.get("option[value='1']").contains("Boucle").click()
    cy.get('#save_changes').click()
    cy.url().should('not.include', '/trek/add/')
    cy.get('.content').should('contain', 'Trek number 1')
  })
})