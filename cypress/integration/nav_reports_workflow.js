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
    // Cannot use selectors for sentinel and supervisor messages yet
    cy.get("#id_message_sentinel_predefined").should("not.be.visible")
    cy.get("#id_message_sentinel").should("not.be.visible")
    cy.get("#id_message_supervisor").should("not.be.visible")
    // Change selected status to resolved
    cy.get("#id_status").select("3")
    // Can use selectors for sentinel messages
    cy.get("#id_message_sentinel_predefined").should("be.visible")
    cy.get("#id_message_sentinel").should("be.visible")
    cy.get("#id_message_supervisor").should("not.be.visible")
    // Select a predefined email
    cy.get("#id_message_sentinel_predefined").select("1")
    cy.get("#id_message_sentinel").should("have.value", "Pris en charge par Comm des Comm des Arbres Binaires le 17/05/2022")
    // Remove predefined email
    cy.get("#id_message_sentinel_predefined").select("")
    cy.get("#id_message_sentinel").should("have.value", "")
    // Change selected status back to initial one
    cy.get("#id_status").select("1")
    // Cannot use selectors for sentinel and supervisor messages
    cy.get("#id_message_sentinel_predefined").should("not.be.visible")
    cy.get("#id_message_sentinel").should("not.be.visible")
    cy.get("#id_message_supervisor").should("not.be.visible")
  })
})
