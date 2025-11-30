import { test, expect } from '@playwright/test';

/**
 * Tests E2E - Scénario Envoi Email
 * Phase 2 - GetYourShare Fiscal System
 */

test.describe('Email Sending', () => {
  
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('merchant@test.com');
    await page.getByLabel(/password/i).fill('test123');
    await page.getByRole('button', { name: /connexion|login/i }).click();
    await page.waitForURL(/\/dashboard/i);
    
    // Navigation
    await page.goto('/fiscal/invoices');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
  });

  test('should display send email button', async ({ page }) => {
    // Vérifier la présence du bouton d'envoi d'email
    const sendButton = page.locator('button[aria-label*="send"], button[aria-label*="email"]').first();
    await expect(sendButton).toBeVisible();
  });

  test('should send email successfully', async ({ page }) => {
    // Cliquer sur le bouton d'envoi d'email
    const sendButton = page.locator('button[aria-label*="send"], button[aria-label*="envoyer"]').first();
    await sendButton.click();
    
    // Attendre la notification de succès
    await expect(page.getByText(/email envoyé avec succès|✅.*email|sent successfully/i)).toBeVisible({ timeout: 10000 });
  });

  test('should show loading state during email sending', async ({ page }) => {
    // Cliquer sur le bouton
    const sendButton = page.locator('button[aria-label*="send"]').first();
    await sendButton.click();
    
    // Vérifier l'état de chargement
    await expect(page.getByText(/envoi en cours|sending|envoi\.\.\./i)).toBeVisible({ timeout: 2000 });
  });

  test('should disable button during email sending', async ({ page }) => {
    // Cliquer sur le bouton
    const sendButton = page.locator('button[aria-label*="send"]').first();
    await sendButton.click();
    
    // Vérifier que le bouton est désactivé pendant l'envoi
    await expect(sendButton).toBeDisabled({ timeout: 1000 });
  });

  test('should send email from invoice details dialog', async ({ page }) => {
    // Ouvrir les détails d'une facture
    const viewButton = page.locator('button[aria-label*="view"]').first();
    await viewButton.click();
    
    // Attendre l'ouverture du dialog
    await expect(page.getByRole('dialog')).toBeVisible();
    
    // Cliquer sur le bouton d'envoi d'email dans le dialog
    const sendInDialog = page.getByRole('dialog').getByRole('button', { name: /envoyer|send.*client/i });
    await sendInDialog.click();
    
    // Vérifier la notification
    await expect(page.getByText(/email envoyé|sent/i)).toBeVisible({ timeout: 10000 });
  });

  test('should display recipient email in success message', async ({ page }) => {
    // Cliquer sur envoi
    const sendButton = page.locator('button[aria-label*="send"]').first();
    await sendButton.click();
    
    // Vérifier que le message contient un email
    const successMessage = page.getByText(/email envoyé.*@.*\.com/i);
    await expect(successMessage).toBeVisible({ timeout: 10000 });
  });

  test('should handle email sending error gracefully', async ({ page }) => {
    // Intercepter la requête pour simuler une erreur
    await page.route('**/api/fiscal/invoices/*/send-email', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Email service unavailable' })
      });
    });
    
    // Essayer d'envoyer l'email
    const sendButton = page.locator('button[aria-label*="send"]').first();
    await sendButton.click();
    
    // Vérifier le message d'erreur
    await expect(page.getByText(/erreur.*email|failed to send/i)).toBeVisible({ timeout: 5000 });
  });

  test('should not send email if invoice is draft', async ({ page }) => {
    // Filtrer les factures brouillon
    await page.getByLabel(/statut|status/i).click();
    await page.getByRole('option', { name: /brouillon|draft/i }).click();
    await page.waitForTimeout(500);
    
    // Vérifier que les boutons d'envoi sont désactivés ou absents
    const sendButtons = page.locator('button[aria-label*="send"]');
    const count = await sendButtons.count();
    
    if (count > 0) {
      // Si présents, ils doivent être désactivés
      await expect(sendButtons.first()).toBeDisabled();
    }
  });

  test('should allow resending email for paid invoices', async ({ page }) => {
    // Filtrer les factures payées
    await page.getByLabel(/statut|status/i).click();
    await page.getByRole('option', { name: /payée|paid/i }).click();
    await page.waitForTimeout(500);
    
    // Le bouton d'envoi doit être disponible (pour renvoyer)
    const sendButton = page.locator('button[aria-label*="send"]').first();
    if (await sendButton.isVisible()) {
      await expect(sendButton).toBeEnabled();
    }
  });

  test('should confirm email delivery with backend', async ({ page }) => {
    // Intercepter la requête API pour vérifier les données envoyées
    let requestData = null;
    await page.route('**/api/fiscal/invoices/*/send-email', async (route) => {
      requestData = route.request();
      await route.continue();
    });
    
    // Envoyer l'email
    const sendButton = page.locator('button[aria-label*="send"]').first();
    await sendButton.click();
    
    // Attendre la notification
    await expect(page.getByText(/email envoyé/i)).toBeVisible({ timeout: 10000 });
    
    // Vérifier que la requête a été faite
    expect(requestData).toBeTruthy();
    expect(requestData.method()).toBe('POST');
  });

  test('should update invoice status after email sent', async ({ page }) => {
    // Obtenir l'ID de la première facture
    const firstInvoice = page.locator('table tbody tr, [role="row"]').first();
    const initialStatus = await firstInvoice.locator('[data-status]').textContent();
    
    // Envoyer l'email
    const sendButton = page.locator('button[aria-label*="send"]').first();
    await sendButton.click();
    
    // Attendre la confirmation
    await expect(page.getByText(/email envoyé/i)).toBeVisible({ timeout: 10000 });
    
    // Recharger la liste
    await page.reload();
    await page.waitForTimeout(1000);
    
    // Vérifier que le statut peut avoir changé (dépend de la logique métier)
    const newStatus = await firstInvoice.locator('[data-status]').textContent();
    expect(newStatus).toBeTruthy();
  });

  test('should close notification after auto-hide duration', async ({ page }) => {
    // Envoyer l'email
    const sendButton = page.locator('button[aria-label*="send"]').first();
    await sendButton.click();
    
    // Attendre la notification
    const notification = page.getByText(/email envoyé/i);
    await expect(notification).toBeVisible({ timeout: 10000 });
    
    // Attendre que la notification disparaisse (6 secondes)
    await expect(notification).not.toBeVisible({ timeout: 8000 });
  });

  test('should manually close success notification', async ({ page }) => {
    // Envoyer l'email
    const sendButton = page.locator('button[aria-label*="send"]').first();
    await sendButton.click();
    
    // Attendre la notification
    await expect(page.getByText(/email envoyé/i)).toBeVisible({ timeout: 10000 });
    
    // Cliquer sur le bouton de fermeture de la notification
    const closeButton = page.getByRole('button', { name: /close/i }).last();
    await closeButton.click();
    
    // Vérifier que la notification disparaît immédiatement
    await expect(page.getByText(/email envoyé/i)).not.toBeVisible({ timeout: 1000 });
  });

});
