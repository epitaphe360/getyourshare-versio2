// tests/e2e/auth.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Authentication Flow', () => {
  
  test('should display login page', async ({ page }) => {
    await page.goto('/login');
    
    await expect(page.locator('h1')).toContainText(/connexion|login/i);
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should show validation errors for empty form', async ({ page }) => {
    await page.goto('/login');
    
    await page.click('button[type="submit"]');
    
    // Should not navigate away
    await expect(page).toHaveURL(/.*login/);
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('input[name="email"]', 'admin@getyourshare.com');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard/, { timeout: 10000 });
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('input[name="email"]', 'wrong@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');
    
    // Should show error message
    await expect(page.locator('.alert, .error-message')).toBeVisible({ timeout: 5000 });
  });

  test('should navigate to register page', async ({ page }) => {
    await page.goto('/login');
    
    await page.click('a[href*="register"]');
    
    await expect(page).toHaveURL(/.*register/);
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[name="email"]', 'admin@getyourshare.com');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL(/.*dashboard/, { timeout: 10000 });
    
    // Logout
    await page.click('button:has-text("Déconnexion"), a:has-text("Déconnexion")');
    
    // Should redirect to login
    await expect(page).toHaveURL(/.*login/, { timeout: 5000 });
  });

});

test.describe('Role-based Access', () => {
  
  test('should redirect admin to admin dashboard', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'admin@getyourshare.com');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL(/.*dashboard\/admin/, { timeout: 10000 });
  });

  test('should block access to admin routes for non-admin', async ({ page }) => {
    // Login as merchant
    await page.goto('/login');
    await page.fill('input[name="email"]', 'merchant@getyourshare.com');
    await page.fill('input[type="password"]', 'merchant123');
    await page.click('button[type="submit"]');
    
    // Try to access admin route
    await page.goto('/dashboard/admin');
    
    // Should redirect or show error
    const url = page.url();
    expect(url).not.toContain('/dashboard/admin');
  });

});
