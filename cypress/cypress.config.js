const { defineConfig } = require('cypress')

module.exports = defineConfig({
  projectId: 'ktpy7v',
  e2e: {
    baseUrl: 'http://geotrek.local:8000',
    supportFile: 'support/e2e.js',
    specPattern: 'e2e/**/*.cy.js',
    allowCypressEnv: false,
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
    videoCompression: true,
    screenshotOnRunFailure: true,
    chromeWebSecurity: false,
    defaultCommandTimeout: 50000,
    setupNodeEvents(on, config) {
      on('before:browser:launch', (browser = {}, launchOptions) => {
        if (browser.family === 'chromium' && browser.name !== 'electron') {
          // Enable WebGL for MapLibre GL JS
          launchOptions.args.push(
            '--ignore-gpu-blocklist',
            '--enable-webgl',
            '--enable-webgl2',
            '--use-gl=angle',
            '--use-angle=swiftshader',
            '--disable-dev-shm-usage',
            '--ignore-certificate-errors',
          )
        }
        if (browser.family === 'firefox') {
          // Firefox WebGL settings
          launchOptions.preferences['webgl.disabled'] = false
          launchOptions.preferences['webgl.force-enabled'] = true
        }
        return launchOptions
      })
    }
  },
});
