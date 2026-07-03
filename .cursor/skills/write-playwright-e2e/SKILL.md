---
name: write-playwright-e2e
description: Writes Playwright end-to-end tests using accessible locators (getByLabel, getByRole) and full user journeys such as signup, login, logout, and error paths. Use when the user asks to write an e2e test, a Playwright test, or an end-to-end test.
---

# write-playwright-e2e

**Trigger**: "e2e test", "playwright test", "end-to-end"

**Template**:
```typescript
import { test, expect } from '@playwright/test';

test.describe('User authentication', () => {
  test('user can sign up and log in', async ({ page }) => {
    // Sign up
    await page.goto('/signup');
    await page.getByLabel('Email').fill('e2e-test@example.com');
    await page.getByLabel('Password').fill('SecureP@ss1');
    await page.getByRole('button', { name: 'Create account' }).click();
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText('Welcome')).toBeVisible();

    // Log out
    await page.getByRole('button', { name: 'Sign out' }).click();
    await expect(page).toHaveURL('/login');

    // Log back in
    await page.getByLabel('Email').fill('e2e-test@example.com');
    await page.getByLabel('Password').fill('SecureP@ss1');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await expect(page).toHaveURL('/dashboard');
  });

  test('shows error on invalid credentials', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill('wrong@example.com');
    await page.getByLabel('Password').fill('wrongpassword');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await expect(page.getByRole('alert')).toContainText('Invalid credentials');
  });
});
```
