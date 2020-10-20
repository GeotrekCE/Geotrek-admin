Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false
})

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

  it('Create trek', () => {
    cy.visit('http://localhost:8000/trek/list')
    cy.server()
    cy.route('/api/graph.json').as('graph')
    cy.get("a.btn-success[href='/trek/add/']").contains('Add a new trek').click()
    cy.wait('@graph')
    cy.get("a.linetopology-control").click()
    cy.get('.leaflet-map-pane')
      .click(405, 290)
      .click(450, 150);
    cy.get("input[name='name_en']").type('Trek number 1')
    cy.get("a[href='#name_fr']").click()
    cy.get("input[name='name_fr']").type('Randonnée numéro 1')
    cy.get("input[id='id_review']").click()
    cy.get("input[id='id_departure_en']").type('Departure')
    cy.get("a[href='#departure_fr']").click()
    cy.get("input[id='id_departure_fr']").type('Départ')
    cy.get("input[id='id_arrival_en']").type('Arrival')
    cy.get("a[href='#arrival_fr']").click()
    cy.get("input[id='id_arrival_fr']").type('Arrivée')
    cy.get("input[id='id_duration']").type('100')
    cy.get("select[id='id_practice']").select("Cycling")
    cy.get("select[id='id_difficulty']").select("Very hard")
    cy.get("select[id='id_route']").select("Loop")
    cy.setTinyMceContent('id_access_en', 'Access number 1');
    cy.setTinyMceContent('id_description_teaser_en', 'Description teaser number 1')
    cy.setTinyMceContent('id_ambiance_en', 'Ambiance number 1')
    cy.setTinyMceContent('id_description_en', 'Description number 1')
    cy.get('#save_changes').click()
    cy.url().should('not.include', '/trek/add/')
    cy.get('.content').should('contain', 'Trek number 1')
  })
  it('List trek waiting for publication', () => {
    cy.visit('http://localhost:8000/trek/list')
    cy.get("a[title='Trek number 1']").should('have.length', 1)
    cy.get("span.badge-warning[title='Waiting for publication']").should('have.length', 1)
  })
  it('Change trek waiting for publication', () => {
    cy.visit('http://localhost:8000/trek/list')
    cy.get("a[title='Trek number 1']").should('have.attr', 'href')
      .then((href) => {
        cy.visit(href)
    })
    cy.get("div.alert-warning").contains("Waiting for publication").should('have.length', 1)
    cy.get("a.btn-primary").contains("Update").click()
    cy.get("input[id='id_review']").check()
    cy.get("input[name='published_en']").click()
    cy.get("input[id='id_published_en']").check()
    cy.get('#save_changes').click()
  })
})
