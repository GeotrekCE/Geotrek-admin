describe('Nav tabs properties/attachments', () => {
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

  it('Use tabs', () => {
    cy.visit('http://localhost:8000/trek/list')
    cy.get("a[title='Trek number 1']").should('have.attr', 'href')
      .then((href) => {
        cy.visit(href)
    })
    cy.get("a#tab-properties").should('contain', '.active')
    cy.get("a#tab-attachments-accessibility").should('not.contain', '.active')
    cy.get("a#tab-attachments-accessibility").click()
    cy.get("a#tab-attachments-accessibility").should('contain', '.active')
    cy.get("a#tab-properties").should('not.contain', '.active')
  })

})