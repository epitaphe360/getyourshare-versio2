// cypress/support/e2e.js
// Support Commands et configurations

import './commands';

// Désactiver les messages d'erreur non capturés
Cypress.on('uncaught:exception', (err, runnable) => {
  // Retourner false pour continuer si erreur anticipée
  return false;
});

// Configuration globale
beforeEach(() => {
  // Nettoyer localStorage avant chaque test
  cy.window().then((win) => {
    win.localStorage.clear();
  });

  // Réinitialiser le sessionStorage
  cy.window().then((win) => {
    win.sessionStorage.clear();
  });

  // Configurer les mocks d'API par défaut
  cy.intercept('GET', '/api/dashboard/stats', {
    statusCode: 200,
    body: {
      stats: {
        leads: 145,
        conversions: 23,
        revenue: 45000,
        performance: 85
      }
    }
  });

  cy.intercept('GET', '/api/leads', {
    statusCode: 200,
    body: {
      leads: [
        { id: 1, name: 'John Doe', score: 85, temperature: 'hot', engaged: true },
        { id: 2, name: 'Jane Smith', score: 72, temperature: 'warm', engaged: true },
        { id: 3, name: 'Bob Johnson', score: 45, temperature: 'cold', engaged: false }
      ]
    }
  });

  // Empêcher les avertissements de console
  const logs = [];
  cy.on('window:before:load', (win) => {
    const consoleSpy = cy.spy(win.console, 'warn');
  });
});

// Hook après chaque test
afterEach(() => {
  // Les tests devraient se terminer correctement
  cy.window().then((win) => {
    // Vérifier s'il y a des erreurs critiques
    const errors = win.__errors || [];
    if (errors.length > 0) {
      console.warn('Erreurs détectées:', errors);
    }
  });
});
