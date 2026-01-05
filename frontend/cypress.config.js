// cypress.config.js
// Configuration Cypress pour tests E2E Commercial Dashboard

const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    specPattern: 'cypress/e2e/**/*.cy.js',
    supportFile: false,
    
    setupNodeEvents(on, config) {
      // Implémentez les événements du nœud ici
    },

    // Configuration des timeouts
    responseTimeout: 10000,
    requestTimeout: 10000,
    defaultCommandTimeout: 5000,
    execTimeout: 60000,
    pageLoadTimeout: 30000,
    taskTimeout: 60000,

    // Configuration du navigateur
    chromeWebSecurity: false,
    videoOnFailure: true,
    screenshotOnRunFailure: true,

    // Viewports pour responsive testing
    viewportWidth: 1280,
    viewportHeight: 720,

    // Autres options
    retries: {
      runMode: 2,
      openMode: 0
    },

    // Slowdown pour debug
    slowTestThreshold: 5000,
  },

  component: {
    devServer: {
      framework: 'react',
      bundler: 'vite',
    },
  },
});
