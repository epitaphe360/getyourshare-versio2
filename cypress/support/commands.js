// cypress/support/commands.js
// Commandes Cypress personnalisées

// Commande pour attendre le chargement du dashboard
Cypress.Commands.add('waitForDashboard', () => {
  cy.get('[class*="dashboard"]', { timeout: 10000 }).should('exist');
  cy.get('[class*="commercial-dashboard"]', { timeout: 10000 }).should('exist');
});

// Commande pour vérifier un composant
Cypress.Commands.add('shouldComponentBeVisible', (componentName) => {
  cy.get(`[data-testid="${componentName}"]`, { timeout: 5000 })
    .should('exist')
    .and('be.visible');
});

// Commande pour cliquer et attendre
Cypress.Commands.add('clickAndWait', (selector) => {
  cy.get(selector).click();
  cy.wait(500);
});

// Commande pour taper avec délai
Cypress.Commands.add('typeWithDelay', (selector, text) => {
  cy.get(selector).type(text, { delay: 100 });
});

// Commande pour vérifier localStorage
Cypress.Commands.add('checkLocalStorage', (key, expectedValue) => {
  cy.window().then((win) => {
    const value = win.localStorage.getItem(key);
    expect(value).to.include(expectedValue || '');
  });
});

// Commande pour vérifier les erreurs console
Cypress.Commands.add('checkForConsoleErrors', () => {
  cy.window().then((win) => {
    const logs = win.__logs || [];
    const errors = logs.filter(log => log.level === 'error');
    expect(errors).to.have.length(0);
  });
});

// Commande pour attendre une animation
Cypress.Commands.add('waitForAnimation', (selector) => {
  cy.get(selector).should('be.visible');
  cy.wait(1000); // Attendre l'animation Framer Motion
});

// Commande pour login (si nécessaire)
Cypress.Commands.add('login', (email = 'test@example.com', password = 'password') => {
  cy.visit('/login');
  cy.get('[data-testid="email-input"]').type(email);
  cy.get('[data-testid="password-input"]').type(password);
  cy.get('[data-testid="login-button"]').click();
  cy.url().should('include', '/dashboard');
});

// Commande pour attendre le chargement d'un élément
Cypress.Commands.add('waitForElement', (selector, timeout = 5000) => {
  cy.get(selector, { timeout }).should('exist').and('be.visible');
});
