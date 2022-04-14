describe('Nav reports workflow', () => {
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

  it('Handles resolved intervention reports', () => {
    cy.visit('http://localhost:8000/report/list')
    cy.get("a[title='test@resolved.fr']").should('have.attr', 'href')
      .then((href) => {
        cy.visit(href)
      })
    cy.get(".btn.btn-primary.ml-auto").click()
    cy.get("#id_message_sentinel_predefined").should("not.be.visible")
    cy.get("#id_message_sentinel").should("not.be.visible")
    cy.get("#id_status").select("3")
    cy.get("#id_message_sentinel_predefined").should("be.visible")
    cy.get("#id_message_sentinel").should("be.visible")
  })
})
