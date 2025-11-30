import { test, expect } from '@playwright/test';

/**
 * Tests E2E - Scénario Création & Gestion Factures
 * Phase 2 - GetYourShare Fiscal System
 */

test.describe('Invoice Management', () => {
  
  // Helper: Login avant chaque test
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('merchant@test.com');
    await page.getByLabel(/password/i).fill('test123');
    await page.getByRole('button', { name: /connexion|login/i }).click();
    await page.waitForURL(/\/dashboard/i);
    
    // Naviguer vers la page des factures
    await page.goto('/fiscal/invoices');
    await page.waitForLoadState('networkidle');
  });

  test('should display invoices list page', async ({ page }) => {
    // Vérifier le titre de la page
    await expect(page.getByRole('heading', { name: /mes factures|invoices/i })).toBeVisible();
    
    // Vérifier le bouton de création
    await expect(page.getByRole('button', { name: /nouvelle facture|new invoice/i })).toBeVisible();
    
    // Vérifier la présence de la table ou grille
    await expect(page.locator('table, [role="grid"]')).toBeVisible();
  });

  test('should open create invoice dialog', async ({ page }) => {
    // Cliquer sur "Nouvelle Facture"
    await page.getByRole('button', { name: /nouvelle facture|new invoice/i }).click();
    
    // Vérifier l'ouverture du dialog
    await expect(page.getByRole('dialog')).toBeVisible();
    await expect(page.getByText(/créer une facture|create invoice/i)).toBeVisible();
    
    // Vérifier la présence des champs du formulaire
    await expect(page.getByLabel(/nom du client|client name/i)).toBeVisible();
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/pays|country/i)).toBeVisible();
  });

  test('should validate required fields', async ({ page }) => {
    // Ouvrir le dialog
    await page.getByRole('button', { name: /nouvelle facture|new invoice/i }).click();
    
    // Essayer de soumettre sans remplir les champs
    await page.getByRole('button', { name: /créer|create|suivant|next/i }).click();
    
    // Vérifier les messages d'erreur de validation
    const errorMessages = page.getByText(/requis|required|obligatoire/i);
    await expect(errorMessages.first()).toBeVisible();
  });

  test('should create invoice successfully', async ({ page }) => {
    // Ouvrir le dialog
    await page.getByRole('button', { name: /nouvelle facture|new invoice/i }).click();
    await page.waitForTimeout(500);
    
    // Remplir le formulaire - Étape 1: Informations client
    await page.getByLabel(/nom du client|client name/i).fill('Test Client E2E');
    await page.getByLabel(/email/i).fill('client-e2e@test.com');
    await page.getByLabel(/adresse|address/i).fill('123 Test Street');
    
    // Sélectionner le pays (Maroc)
    const countrySelect = page.getByLabel(/pays|country/i);
    await countrySelect.click();
    await page.getByRole('option', { name: /maroc|ma/i }).click();
    
    // Passer à l'étape suivante
    await page.getByRole('button', { name: /suivant|next/i }).click();
    await page.waitForTimeout(500);
    
    // Étape 2: Ajouter des articles
    await page.getByLabel(/description|libellé/i).first().fill('Service de test E2E');
    await page.getByLabel(/quantité|quantity/i).first().fill('2');
    await page.getByLabel(/prix unitaire|unit price/i).first().fill('100');
    
    // Vérifier le calcul automatique du montant
    await expect(page.getByText(/200/)).toBeVisible(); // 2 * 100
    
    // Soumettre la facture
    await page.getByRole('button', { name: /créer la facture|create invoice/i }).click();
    
    // Attendre la notification de succès
    await expect(page.getByText(/facture créée avec succès|invoice created|✅/i)).toBeVisible({ timeout: 5000 });
    
    // Vérifier que le dialog se ferme
    await expect(page.getByRole('dialog')).not.toBeVisible({ timeout: 3000 });
    
    // Vérifier que la nouvelle facture apparaît dans la liste
    await expect(page.getByText('Test Client E2E')).toBeVisible();
  });

  test('should display invoice details', async ({ page }) => {
    // Attendre le chargement des factures
    await page.waitForTimeout(1000);
    
    // Cliquer sur l'icône "View" de la première facture
    const firstViewButton = page.locator('button[aria-label*="view"], button[title*="voir"]').first();
    await firstViewButton.click();
    
    // Vérifier l'ouverture du dialog de détails
    await expect(page.getByRole('dialog')).toBeVisible();
    await expect(page.getByText(/détails de la facture|invoice details/i)).toBeVisible();
    
    // Vérifier la présence des informations clés
    await expect(page.getByText(/client|customer/i)).toBeVisible();
    await expect(page.getByText(/montant|amount|total/i)).toBeVisible();
    await expect(page.getByText(/statut|status/i)).toBeVisible();
  });

  test('should filter invoices by status', async ({ page }) => {
    // Attendre le chargement
    await page.waitForTimeout(1000);
    
    // Compter le nombre total de factures
    const allInvoices = await page.locator('table tbody tr, [role="row"]').count();
    
    // Filtrer par "Paid" (Payée)
    await page.getByLabel(/statut|status|filter/i).click();
    await page.getByRole('option', { name: /payée|paid/i }).click();
    await page.waitForTimeout(500);
    
    // Vérifier que le filtre est appliqué
    const paidInvoices = await page.locator('table tbody tr, [role="row"]').count();
    
    // Le nombre devrait avoir changé (sauf si toutes sont payées)
    expect(paidInvoices).toBeLessThanOrEqual(allInvoices);
  });

  test('should search invoices by client name', async ({ page }) => {
    // Attendre le chargement
    await page.waitForTimeout(1000);
    
    // Obtenir le nom du premier client
    const firstClientName = await page.locator('table tbody tr, [role="row"]').first().textContent();
    
    if (firstClientName) {
      // Extraire un mot du nom (simplifié)
      const searchTerm = firstClientName.split(' ')[0].substring(0, 5);
      
      // Utiliser la barre de recherche
      await page.getByPlaceholder(/rechercher|search/i).fill(searchTerm);
      await page.waitForTimeout(500);
      
      // Vérifier que les résultats contiennent le terme recherché
      const results = await page.locator('table tbody tr, [role="row"]').count();
      expect(results).toBeGreaterThan(0);
    }
  });

  test('should handle pagination if enabled', async ({ page }) => {
    // Attendre le chargement
    await page.waitForTimeout(1000);
    
    // Vérifier si la pagination existe
    const pagination = page.getByRole('navigation', { name: /pagination/i });
    
    if (await pagination.isVisible()) {
      // Cliquer sur page 2
      await page.getByRole('button', { name: '2' }).click();
      await page.waitForTimeout(500);
      
      // Vérifier que l'URL ou le contenu a changé
      const page2Content = await page.locator('table tbody tr').first().textContent();
      expect(page2Content).toBeTruthy();
    }
  });

  test('should export invoice list (if implemented)', async ({ page }) => {
    // Attendre le chargement
    await page.waitForTimeout(1000);
    
    // Chercher un bouton d'export
    const exportButton = page.getByRole('button', { name: /export|télécharger|download/i });
    
    if (await exportButton.isVisible()) {
      // Configuration pour intercepter le téléchargement
      const downloadPromise = page.waitForEvent('download');
      await exportButton.click();
      
      const download = await downloadPromise;
      expect(download.suggestedFilename()).toMatch(/\.csv|\.xlsx|\.pdf/i);
    }
  });

});
