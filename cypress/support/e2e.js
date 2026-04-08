// ***********************************************************
// This example support/e2e.js is processed and
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

// Handle uncaught exceptions from cross-origin scripts (e.g., map tiles, external resources)
// This prevents tests from failing due to errors in third-party scripts
Cypress.on('uncaught:exception', (err, runnable) => {
  // Return false to prevent Cypress from failing the test on cross-origin script errors
  // These errors typically come from map tile providers or other external resources
  if (err.message.includes('Script error')) {
    return false
  }
  // Ignore maplibregl not defined errors that can occur during session transitions
  // This happens when the page is reloaded and MapLibre GL JS hasn't loaded yet
  if (err.message.includes('maplibregl is not defined')) {
    return false
  }
  // Let other errors fail the test
  return true
})
