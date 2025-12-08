// tests/e2e/dashboards.spec.js
const { test, expect } = require('@playwright/test');

// Helper function to login
async function loginAs(page, role = 'admin') {
  const credentials = {
    admin: { email: 'admin@getyourshare.com', password: 'admin123' },
    merchant: { email: 'merchant@getyourshare.com', password: 'merchant123' },
    influencer: { email: 'influencer@getyourshare.com', password: 'influencer123' },
    commercial: { email: 'commercial@getyourshare.com', password: 'commercial123' }
  };

  const creds = credentials[role];
  
  await page.goto('/login');
  await page.fill('input[name="email"]', creds.email);
  await page.fill('input[type="password"]', creds.password);
  await page.click('button[type="submit"]');
  
  await expect(page).toHaveURL(/.*dashboard/, { timeout: 10000 });
}

test.describe('Admin Dashboard', () => {
  
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'admin');
    await page.goto('/dashboard/admin');
  });

  test('should display all key metrics', async ({ page }) => {
    // Wait for dashboard to load
    await page.waitForSelector('[data-testid="dashboard-container"], .dashboard', { timeout: 10000 });
    
    // Check for revenue metric
    await expect(page.locator('text=/revenus?|revenue/i')).toBeVisible();
    
    // Check for users metric
    await expect(page.locator('text=/utilisateurs?|users?/i')).toBeVisible();
    
    // Check for conversions metric
    await expect(page.locator('text=/conversions?/i')).toBeVisible();
  });

  test('should display revenue chart', async ({ page }) => {
    // Wait for charts library to load
    await page.waitForTimeout(2000);
    
    // Check for chart container (Recharts uses recharts-wrapper class)
    const chartExists = await page.locator('.recharts-wrapper, [class*="chart"]').count();
    expect(chartExists).toBeGreaterThan(0);
  });

  test('should display users table', async ({ page }) => {
    await page.waitForSelector('table, .table-container', { timeout: 10000 });
    
    const tableExists = await page.locator('table').count();
    expect(tableExists).toBeGreaterThan(0);
  });

  test('should navigate to users management', async ({ page }) => {
    await page.click('a:has-text("Utilisateurs"), a[href*="users"]');
    
    await expect(page).toHaveURL(/.*users/, { timeout: 5000 });
  });

});

test.describe('Merchant Dashboard', () => {
  
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'merchant');
    await page.goto('/dashboard/merchant');
  });

  test('should display merchant metrics', async ({ page }) => {
    await page.waitForSelector('[data-testid="dashboard-container"], .dashboard', { timeout: 10000 });
    
    // Check for products/campaigns metrics
    await expect(page.locator('text=/produits?|products?|campagnes?|campaigns?/i')).toBeVisible();
  });

  test('should allow creating a product', async ({ page }) => {
    await page.click('a:has-text("Produits"), a[href*="products"]');
    
    const createButton = page.locator('button:has-text("Créer"), button:has-text("Ajouter"), a:has-text("Nouveau")');
    if (await createButton.count() > 0) {
      await createButton.first().click();
      await expect(page).toHaveURL(/.*create|new/, { timeout: 5000 });
    }
  });

});

test.describe('Influencer Dashboard', () => {
  
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'influencer');
    await page.goto('/dashboard/influencer');
  });

  test('should display earnings metrics', async ({ page }) => {
    await page.waitForSelector('[data-testid="dashboard-container"], .dashboard', { timeout: 10000 });
    
    // Check for earnings/commissions
    await expect(page.locator('text=/gains?|earnings?|commissions?/i')).toBeVisible();
  });

  test('should display affiliate links', async ({ page }) => {
    await page.click('a:has-text("Liens"), a[href*="links"]');
    
    await expect(page).toHaveURL(/.*links/, { timeout: 5000 });
  });

});

test.describe('Commercial Dashboard', () => {
  
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'commercial');
    await page.goto('/dashboard/commercial');
  });

  test('should display CRM metrics', async ({ page }) => {
    await page.waitForSelector('[data-testid="dashboard-container"], .dashboard', { timeout: 10000 });
    
    // Check for leads/pipeline metrics
    await expect(page.locator('text=/leads?|prospects?|pipeline/i')).toBeVisible();
  });

  test('should display leads table', async ({ page }) => {
    const tableExists = await page.locator('table').count();
    expect(tableExists).toBeGreaterThan(0);
  });

});
