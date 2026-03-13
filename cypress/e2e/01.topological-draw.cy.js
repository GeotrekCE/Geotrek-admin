describe('Topological draw test', () => {
    beforeEach(() => {
        cy.visit('/');
    });

    it('should display the list page', () => {
        cy.get('body').should('be.visible');
    });
});