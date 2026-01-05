import { test, expect } from '@playwright/test';

/**
 * Tests E2E - Scénario Génération PDF
 * Phase 2 - GetYourShare Fiscal System
 */

test.describe('PDF Generation', () => {
  
  // Helper: Login et navigation
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('merchant@test.com');
    await page.getByLabel(/password/i).fill('test123');
    await page.getByRole('button', { name: /connexion|login/i }).click();
    await page.waitForURL(/\/dashboard/i);
    
    await page.goto('/fiscal/invoices');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
  });

  test('should display PDF generation button', async ({ page }) => {
    // Vérifier la présence du bouton PDF sur la première facture
    const pdfButton = page.locator('button[aria-label*="pdf"], button[title*="pdf"]').first();
    await expect(pdfButton).toBeVisible();
  });

  test('should generate and display PDF inline', async ({ page }) => {
    // Cliquer sur le bouton de génération PDF
    const pdfButton = page.locator('button[aria-label*="pdf"], button[title*="télécharger"]').first();
    await pdfButton.click();
    
    // Attendre l'ouverture du dialog PDFViewer
    await expect(page.getByRole('dialog')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText(/aperçu pdf|pdf preview/i)).toBeVisible();
    
    // Vérifier la présence du canvas PDF (react-pdf)
    await expect(page.locator('canvas')).toBeVisible({ timeout: 5000 });
    
    // Vérifier les contrôles du viewer
    await expect(page.getByRole('button', { name: /zoom/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /télécharger|download/i })).toBeVisible();
  });

  test('should show loading state during PDF generation', async ({ page }) => {
    // Cliquer sur le bouton PDF
    const pdfButton = page.locator('button[aria-label*="pdf"]').first();
    await pdfButton.click();
    
    // Vérifier l'affichage du loader
    await expect(page.getByText(/chargement du pdf|loading|génération/i)).toBeVisible({ timeout: 2000 });
  });

  test('should navigate between PDF pages', async ({ page }) => {
    // Générer le PDF
    await page.locator('button[aria-label*="pdf"]').first().click();
    await page.waitForSelector('canvas', { timeout: 10000 });
    
    // Vérifier les informations de pagination
    const paginationText = await page.getByText(/page \d+ \/ \d+/i).textContent();
    expect(paginationText).toMatch(/page/i);
    
    // Si le PDF a plusieurs pages, tester la navigation
    if (paginationText && paginationText.includes('/ 2')) {
      // Cliquer sur "Page suivante"
      await page.getByRole('button', { name: /next|suivant/i }).click();
      await page.waitForTimeout(500);
      
      // Vérifier que la page a changé
      await expect(page.getByText(/page 2/i)).toBeVisible();
      
      // Retour à la page 1
      await page.getByRole('button', { name: /previous|précédent/i }).click();
      await page.waitForTimeout(500);
      await expect(page.getByText(/page 1/i)).toBeVisible();
    }
  });

  test('should zoom in and out on PDF', async ({ page }) => {
    // Générer le PDF
    await page.locator('button[aria-label*="pdf"]').first().click();
    await page.waitForSelector('canvas', { timeout: 10000 });
    
    // Obtenir le zoom initial
    const initialZoom = await page.getByText(/\d+%/).textContent();
    expect(initialZoom).toMatch(/100%/);
    
    // Zoom avant
    await page.getByRole('button', { name: /zoom.*in|agrandir/i }).click();
    await page.waitForTimeout(500);
    
    // Vérifier que le zoom a augmenté
    const zoomedIn = await page.getByText(/\d+%/).textContent();
    expect(parseInt(zoomedIn)).toBeGreaterThan(100);
    
    // Zoom arrière
    await page.getByRole('button', { name: /zoom.*out|réduire/i }).click();
    await page.waitForTimeout(500);
  });

  test('should download PDF from viewer', async ({ page }) => {
    // Générer le PDF
    await page.locator('button[aria-label*="pdf"]').first().click();
    await page.waitForSelector('canvas', { timeout: 10000 });
    
    // Préparer l'interception du téléchargement
    const downloadPromise = page.waitForEvent('download', { timeout: 10000 });
    
    // Cliquer sur le bouton de téléchargement dans le viewer
    const downloadButtons = page.getByRole('button', { name: /télécharger|download/i });
    await downloadButtons.last().click(); // Le dernier pour éviter le bouton de la liste
    
    // Vérifier que le téléchargement a démarré
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/\.pdf$/i);
    expect(download.suggestedFilename()).toContain('Facture');
  });

  test('should close PDF viewer', async ({ page }) => {
    // Générer le PDF
    await page.locator('button[aria-label*="pdf"]').first().click();
    await page.waitForSelector('canvas', { timeout: 10000 });
    
    // Vérifier que le dialog est ouvert
    await expect(page.getByRole('dialog')).toBeVisible();
    
    // Fermer le viewer
    await page.getByRole('button', { name: /fermer|close/i }).last().click();
    
    // Vérifier que le dialog est fermé
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });

  test('should handle PDF generation error gracefully', async ({ page }) => {
    // Intercepter la requête API pour simuler une erreur
    await page.route('**/api/fiscal/invoices/*/generate-pdf', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' })
      });
    });
    
    // Essayer de générer le PDF
    await page.locator('button[aria-label*="pdf"]').first().click();
    
    // Vérifier le message d'erreur
    await expect(page.getByText(/erreur.*pdf|error/i)).toBeVisible({ timeout: 5000 });
  });

  test('should display PDF with correct content', async ({ page }) => {
    // Générer le PDF
    await page.locator('button[aria-label*="pdf"]').first().click();
    await page.waitForSelector('canvas', { timeout: 10000 });
    
    // Attendre le rendu complet
    await page.waitForTimeout(2000);
    
    // Vérifier que le canvas a bien du contenu (non vide)
    const canvas = page.locator('canvas').first();
    const bbox = await canvas.boundingBox();
    
    expect(bbox).toBeTruthy();
    expect(bbox.width).toBeGreaterThan(400);
    expect(bbox.height).toBeGreaterThan(500);
  });

  test('should show success notification after PDF generation', async ({ page }) => {
    // Cliquer sur le bouton PDF
    await page.locator('button[aria-label*="pdf"]').first().click();
    
    // Attendre et vérifier le snackbar de succès
    await expect(page.getByText(/pdf généré avec succès|✅/i)).toBeVisible({ timeout: 5000 });
  });

});
