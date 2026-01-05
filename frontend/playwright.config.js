import { defineConfig, devices } from '@playwright/test';

/**
 * Configuration Playwright pour tests E2E GetYourShare
 * Phase 2 - Tests système fiscal
 */
export default defineConfig({
  testDir: './e2e',
  
  // Timeout configuration
  timeout: 30 * 1000, // 30 secondes par test
  expect: {
    timeout: 5000, // 5 secondes pour les assertions
  },
  
  // Retry failed tests
  fullyParallel: true,
  forbidOnly: !!process.env.CI, // Empêche .only en CI
  retries: process.env.CI ? 2 : 0, // Retry en CI seulement
  workers: process.env.CI ? 1 : undefined,
  
  // Reporting
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results.json' }],
    ['list']
  ],
  
  // Configuration globale
  use: {
    // URL de base de l'application
    baseURL: 'http://localhost:3000',
    
    // Traces et screenshots
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    
    // Timeouts
    actionTimeout: 10000,
    navigationTimeout: 15000,
  },

  // Configuration des projets (navigateurs)
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    
    // Tests mobile (optionnel)
    // {
    //   name: 'Mobile Chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
    // {
    //   name: 'Mobile Safari',
    //   use: { ...devices['iPhone 12'] },
    // },
  ],

  // Serveur de développement (démarre automatiquement)
  webServer: {
    command: 'npm start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000, // 2 minutes pour démarrer React
    stdout: 'pipe',
    stderr: 'pipe',
  },
});
