describe('Change language', () => {
    beforeEach(() => {
        const username = 'admin';
        const password = 'admin';
        cy.loginByCSRF(username, password);
    });

    it('Can change language', () => {
        cy.visit('/path/list');
        cy.get("a.dropdown-toggle").contains('admin').click();
        cy.get("button.dropdown-item[value='fr']").click();
        cy.get("a.btn-success[href='/path/add/']").contains('Ajouter');
        cy.url().should('include', '/path/list/');
        cy.get("a.dropdown-toggle").contains('admin').click();
        cy.get("button.dropdown-item[value='en']").click();
    });
});
