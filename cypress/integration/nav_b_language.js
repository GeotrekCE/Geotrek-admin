describe('Create path', () => {
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

  it('Change language', () => {
    cy.visit('/path/list')
    cy.get("a.dropdown-toggle").contains('admin').click()
    cy.get("button.language-menu-item[value='fr']").click()
    cy.get("a.btn-success[href='/path/add/']").contains('Ajouter un tronçon')
    cy.url().should('include', '/path/list/')
    cy.get("a.dropdown-toggle").contains('admin').click()
    cy.get("button.language-menu-item[value='en']").click()
  })

})
