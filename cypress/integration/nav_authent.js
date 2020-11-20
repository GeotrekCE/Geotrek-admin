describe('Login from home page / admin page', () => {
  it('Redirects to login page.', () => {
    cy.visit('http://localhost:8000')
    cy.url().should('include', '/login/?next=/')
    cy.get('form')
    cy.contains("Username:")
    cy.get('[name="username"]')
    })

  it('Fail to login', () => {
    cy.visit('http://localhost:8000/login/?next=/')
    cy.get('[name="username"]')
      .type('fake')
      .should('have.value', 'fake')
    cy.get('[name="password"]')
      .type('password')
      .should('have.value', 'password')
    cy.get("button[type='submit']").click()
    cy.url().should('include', '/login/?next=/')
  })

  it('Login', () => {
    cy.visit('http://localhost:8000/login/?next=/')
    cy.get('[name="username"]')
      .type('admin')
      .should('have.value', 'admin')
    cy.get('[name="password"]')
      .type('admin')
      .should('have.value', 'admin')
    cy.get("button[type='submit']").click()
    cy.url().should('include', '/path/list/')
    cy.url().should('not.include', '/login/?next=/')
  })

  it('Redirects to admin login page.', () => {
    cy.visit('http://localhost:8000/admin')
    cy.url().should('include', '/login/?next=/')
    cy.get('form')
    cy.contains("Username:")
    cy.get('[name="username"]')
  })

  it('Login admin', () => {
    cy.visit('http://localhost:8000/admin/')
    cy.get('[name="username"]')
      .type('admin')
      .should('have.value', 'admin')
    cy.get('[name="password"]')
      .type('admin')
      .should('have.value', 'admin')
    cy.get("input[type='submit']").click()
    cy.url().should('include', '/admin/')
    cy.url().should('not.include', '/login/?next=/')
  })
})


describe('Logout', () => {
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

  it('Logout', () => {
    cy.visit('http://localhost:8000/')
    cy.url().should('include', '/path/list/')
    cy.get("a.dropdown-toggle").contains('admin').click()
    cy.get("a[href='/logout/']").click()
    cy.url().should('include', '/login/')
  })


  it('Logout admin', () => {
    cy.visit('http://localhost:8000/admin/')
    cy.get("a[href='/admin/logout/']").click()
    cy.url().should('include', '/admin/logout/')
  })
})
