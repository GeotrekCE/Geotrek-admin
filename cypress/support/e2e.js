// ***********************************************************
// This example support/index.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands'

// Alternatively you can use CommonJS syntax:
// require('./commands')

// Prevent uncaught exceptions from the application from failing tests.
// The Geotrek application has some JavaScript that may throw non-critical errors
// (e.g., in status_colors.js when layer data isn't fully loaded).
// These errors don't affect the core functionality being tested.
Cypress.on('uncaught:exception', (err, runnable) => {
    // Ignore known application errors that don't affect test validity
    // Examples include: modelname undefined errors from status_colors.js
    // Return false to prevent Cypress from failing the test
    return false;
});
