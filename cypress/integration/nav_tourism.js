describe('Create tourism event', () => {
  before(() => {
    const username = 'admin'
    const password = 'admin'

    cy.loginByCSRF(username, password)
      .then((resp) => {
        expect(resp.status).to.eq(200)
      })
  })

  beforeEach(() => {
    cy.setCookie('django_language', 'en');
    Cypress.Cookies.preserveOnce('sessionid', 'csrftoken');
  });

  it('Should dynamicly show/hidde participant number', () => {
    cy.visit('/touristicevent/add/').get("#modelfields").scrollTo('bottom');
    // check initially hidden
    cy.get('#div_id_participant_number').should("not.be.visible");
    // check toggle hide/show
    cy.get('#id_bookable').check({ force: true });
    cy.get('#div_id_participant_number').should("be.visible");
    cy.get('#id_bookable').uncheck({ force: true });
    cy.get('#div_id_participant_number').should("not.be.visible");
  })
})
