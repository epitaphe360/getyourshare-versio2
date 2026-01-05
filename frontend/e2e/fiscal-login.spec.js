import { test, expect } from '@playwright/test';

/**
 * Tests E2E - Scénario Login & Navigation
 * Phase 2 - GetYourShare Fiscal System
 */

test.describe('Authentication & Navigation', () => {
  
  test.beforeEach(async ({ page }) => {
    // Naviguer vers la page d'accueil
    await page.goto('/');
  });

  test('should display login page', async ({ page }) => {
    // Vérifier que la page de login s'affiche
    await expect(page).toHaveTitle(/GetYourShare/i);
    
    // Vérifier la présence des champs de connexion
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/password/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /connexion|login/i })).toBeVisible();
  });

  test('should show error with invalid credentials', async ({ page }) => {
    // Remplir le formulaire avec des identifiants invalides
    await page.getByLabel(/email/i).fill('invalid@example.com');
    await page.getByLabel(/password/i).fill('wrongpassword');
    
    // Soumettre le formulaire
    await page.getByRole('button', { name: /connexion|login/i }).click();
    
    // Vérifier le message d'erreur
    await expect(page.getByText(/erreur|invalid|incorrect/i)).toBeVisible();
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    // Remplir le formulaire avec identifiants valides (à adapter selon votre config)
    await page.getByLabel(/email/i).fill('merchant@test.com');
    await page.getByLabel(/password/i).fill('test123');
    
    // Soumettre le formulaire
    await page.getByRole('button', { name: /connexion|login/i }).click();
    
    // Attendre la redirection vers le dashboard
    await page.waitForURL(/\/dashboard|\/home/i, { timeout: 5000 });
    
    // Vérifier que l'utilisateur est connecté
    await expect(page.getByText(/dashboard|tableau de bord/i)).toBeVisible();
  });

  test('should navigate to fiscal invoices page', async ({ page }) => {
    // Se connecter d'abord
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('merchant@test.com');
    await page.getByLabel(/password/i).fill('test123');
    await page.getByRole('button', { name: /connexion|login/i }).click();
    await page.waitForURL(/\/dashboard/i);
    
    // Naviguer vers la page des factures
    await page.getByRole('link', { name: /factures|invoices|fiscal/i }).click();
    
    // Vérifier l'URL
    await expect(page).toHaveURL(/\/fiscal\/invoices/i);
    
    // Vérifier le contenu de la page
    await expect(page.getByText(/mes factures|invoices/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /nouvelle facture|new invoice/i })).toBeVisible();
  });

  test('should persist session after page reload', async ({ page }) => {
    // Se connecter
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('merchant@test.com');
    await page.getByLabel(/password/i).fill('test123');
    await page.getByRole('button', { name: /connexion|login/i }).click();
    await page.waitForURL(/\/dashboard/i);
    
    // Recharger la page
    await page.reload();
    
    // Vérifier que l'utilisateur est toujours connecté
    await expect(page.getByText(/dashboard|tableau de bord/i)).toBeVisible();
    await expect(page).not.toHaveURL(/\/login/i);
  });

  test('should logout successfully', async ({ page }) => {
    // Se connecter
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('merchant@test.com');
    await page.getByLabel(/password/i).fill('test123');
    await page.getByRole('button', { name: /connexion|login/i }).click();
    await page.waitForURL(/\/dashboard/i);
    
    // Cliquer sur le bouton de déconnexion
    await page.getByRole('button', { name: /déconnexion|logout/i }).click();
    
    // Vérifier la redirection vers login
    await page.waitForURL(/\/login|\/$/i);
    await expect(page.getByLabel(/email/i)).toBeVisible();
  });

});
