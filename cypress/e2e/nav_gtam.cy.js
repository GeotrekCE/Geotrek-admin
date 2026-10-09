function zoomUntilEnabled(attemptsLeft = 15) {
    cy.get('form button[type="submit"]').then(($btn) => {
        if ($btn.attr('aria-disabled') === 'true' && attemptsLeft > 0) {
            cy.get('.maplibregl-ctrl-zoom-in').click();
            cy.wait(350);
            zoomUntilEnabled(attemptsLeft - 1);
        }
    });
}

describe('GTAM (Geotrek-admin Mobile)', { testIsolation: false }, () => {
    before(() => {
        cy.clearCookies();
        cy.clearLocalStorage();
        cy.window().then((win) => {
            return new Cypress.Promise((resolve) => {
                const req = win.indexedDB.deleteDatabase('gtam');
                req.onsuccess = () => resolve();
                req.onerror = () => resolve();
                req.onblocked = () => resolve();
            });
        });
    });

    beforeEach(() => {
        cy.mockTiles();
    });

    it('Redirects to login page when accessing /m/', () => {
        cy.visit('/m/');
        cy.url().should('include', '/m/');
        cy.url().should('include', '/login');
        cy.get('[data-testid="login-form"]').should('be.visible');
        cy.get('[data-testid="field-username"]').should('be.visible');
        cy.get('[data-testid="field-password"]').should('be.visible');
    });

    it('Logs in with user and redirects to sync page', () => {
        cy.intercept('POST', '/api/auth/token/').as('authToken');
        cy.intercept('GET', '/api/gtam/config/').as('gtamConfig');

        cy.get('[data-testid="field-username"]')
            .type('admin')
            .should('have.value', 'admin');
        cy.get('[data-testid="field-password"]')
            .type('admin')
            .should('have.value', 'admin');
        cy.get('[data-testid="login-form"] button[type="submit"]').click();

        cy.wait('@authToken').its('response.statusCode').should('eq', 200);
        cy.wait('@gtamConfig').its('response.statusCode').should('eq', 200);

        cy.url().should('include', '/sync');
        cy.get('#sync-down').should('be.visible');
    });

    it('Synchronizes base references and geographic area data', () => {
        cy.intercept('GET', '/api/common/references/').as('commonRef');
        cy.intercept('GET', '/api/infrastructure/references/').as('infraRef');
        cy.intercept('GET', '/api/signage/references/').as('signageRef');
        cy.intercept('GET', '/api/intervention/references/').as('interventionRef');
        cy.intercept('GET', '/api/report/references/').as('reportRef');

        cy.get('#sync-down [data-slot="card"]')
            .first()
            .find('[data-slot="card-footer"] button')
            .click();

        cy.wait([
            '@commonRef',
            '@infraRef',
            '@signageRef',
            '@interventionRef',
            '@reportRef',
        ]);

        cy.get('#sync-down [data-slot="card"]')
            .first()
            .find('[data-slot="alert"]')
            .should('not.exist');

        cy.get('#sync-down a[href$="/sync/data"]').click();
        cy.url().should('include', '/sync/data');
        cy.get('.maplibregl-canvas').should('be.visible');
        cy.get('form button[type="submit"]').should(
            'have.attr',
            'aria-disabled',
            'true'
        );

        zoomUntilEnabled();

        cy.get('form button[type="submit"]').should(
            'have.attr',
            'aria-disabled',
            'false'
        );
        cy.get('input[name="bbox"]').should('not.have.value', '');

        cy.intercept('GET', '**/api/infrastructure/drf/infrastructures*').as('infraData');
        cy.intercept('GET', '**/api/signage/drf/signages*').as('signageData');
        cy.intercept('GET', '**/api/intervention/drf/interventions*').as('interventionData');
        cy.intercept('GET', '**/api/report/drf/reports*').as('reportData');

        cy.get('form button[type="submit"]').click();

        cy.wait([
            '@infraData',
            '@signageData',
            '@interventionData',
            '@reportData',
        ]);

        cy.url().should('match', /\/sync\/?$/);
        cy.get('#sync-down [data-slot="card"]')
            .eq(2)
            .find('[data-slot="alert"]')
            .should('not.exist');
    });

    it('Navigates on the map', () => {
        cy.get('nav[role="navigation"] ul li').first().find('a').click();
        cy.url().should('not.include', '/sync');
        cy.url().should('not.include', '/login');

        cy.get('input[type="search"]').should('be.visible');
        cy.get('.maplibregl-map').should('be.visible');
        cy.get('.maplibregl-canvas').should('be.visible');

        cy.get('.maplibregl-ctrl-zoom-in').click();
        cy.get('.maplibregl-ctrl-zoom-out').click();
        cy.get('.maplibregl-canvas').click('center');
    });

    it('Creates a new signage from GTAM and displays it on the map', () => {
        cy.get('nav[role="navigation"] a[href$="/create"]').click();
        cy.url().should('include', '/create');

        cy.get('a[href$="/data/signage/create"]').click();
        cy.url().should('include', '/data/signage/create');

        cy.get('[data-testid="field-name"]').type('Signalétique GTAM');
        cy.get('[data-testid="field-type"]').click();
        cy.get('[role="option"]').first().click();

        cy.get('button[data-testid="field-geom"]').click();
        cy.get('.maplibregl-canvas').should('be.visible').click('center');
        cy.contains('Longitude :').should('be.visible');

        cy.get('form button[type="submit"]').click();

        cy.url().should('match', /\/data\/signage\/\d+/);
        cy.contains('h2', 'Signalétique GTAM').should('be.visible');

        cy.get('nav[role="navigation"] ul li').first().find('a').click();
        cy.get('.maplibregl-canvas').should('be.visible');
        cy.get('input[type="search"]').type('Signalétique GTAM');
        cy.contains('Signalétique GTAM').should('exist');
    });
});
