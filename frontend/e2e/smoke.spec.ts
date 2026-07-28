// Playwright E2E smoke — student chat shell + login page.
import { test, expect } from '@playwright/test'

const BASE = process.env.E2E_BASE_URL ?? 'http://127.0.0.1:5173'

test.describe('Equa smoke', () => {
  test('chat page shows empty state and input', async ({ page }) => {
    await page.goto(`${BASE}/chat`)
    await expect(page.getByText('Mesaj yazarak başla')).toBeVisible()
    await expect(page.getByLabel('Mesajın')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Gönder' })).toBeVisible()
  })

  test('login page renders demo credentials fields', async ({ page }) => {
    await page.goto(`${BASE}/login`)
    await expect(page.getByRole('heading', { name: 'Equa' })).toBeVisible()
    await expect(page.getByLabel('E-posta')).toBeVisible()
    await expect(page.getByLabel('Şifre')).toBeVisible()
  })

  test('bottom nav exposes check-in and profile', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 })
    await page.goto(`${BASE}/chat`)
    await expect(
      page.getByRole('navigation', { name: 'Mobil navigasyon' }),
    ).toBeVisible()
    await expect(
      page
        .getByRole('navigation', { name: 'Mobil navigasyon' })
        .getByText('Check-in'),
    ).toBeVisible()
    await expect(
      page
        .getByRole('navigation', { name: 'Mobil navigasyon' })
        .getByText('Profil'),
    ).toBeVisible()
  })
})
