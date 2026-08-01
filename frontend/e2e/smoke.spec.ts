// Playwright E2E — critical journeys (auth-aware, happy + negative paths).
import { test, expect, type Page } from '@playwright/test'

const BASE = process.env.E2E_BASE_URL ?? 'http://127.0.0.1:5173'

async function seedStudentAuth(page: Page, opts?: { onboarding?: boolean }) {
  const onboarding = opts?.onboarding ?? true
  await page.addInitScript(
    ([completed]) => {
      localStorage.setItem('equa_access_token', 'e2e-mock-token')
      localStorage.setItem(
        'equa_user',
        JSON.stringify({
          id: '11111111-1111-1111-1111-111111111101',
          tenant_id: '11111111-1111-1111-1111-111111111111',
          email: 'test_student_alpha@equa.dev',
          full_name: 'Test Student',
          role: 'student',
          onboarding_completed: completed,
        }),
      )
    },
    [onboarding],
  )
}

async function seedInstructorAuth(page: Page) {
  await page.addInitScript(() => {
    localStorage.setItem('equa_access_token', 'e2e-mock-token')
    localStorage.setItem(
      'equa_user',
      JSON.stringify({
        id: '11111111-1111-1111-1111-111111111201',
        tenant_id: '11111111-1111-1111-1111-111111111111',
        email: 'coordinator_alpha@equa.dev',
        full_name: 'Coordinator Alpha',
        role: 'instructor',
      }),
    )
  })
}

test.describe('Equa critical journeys', () => {
  test('unauthenticated /chat redirects to login', async ({ page }) => {
    await page.goto(`${BASE}/chat`)
    await expect(page).toHaveURL(/\/login/)
    await expect(page.getByRole('heading', { name: 'Equa' })).toBeVisible()
  })

  test('login page renders credential fields', async ({ page }) => {
    await page.goto(`${BASE}/login`)
    await expect(page.getByRole('heading', { name: 'Equa' })).toBeVisible()
    await expect(page.getByLabel('E-posta')).toBeVisible()
    await expect(page.getByLabel('Şifre')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Giriş yap' })).toBeVisible()
  })

  test('student chat shell with bottom nav', async ({ page }) => {
    await seedStudentAuth(page)
    await page.setViewportSize({ width: 390, height: 844 })
    await page.goto(`${BASE}/chat`)

    await expect(
      page.getByRole('navigation', { name: 'Mobil navigasyon' }),
    ).toBeVisible({ timeout: 10000 })
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

  test('student cannot open institution route', async ({ page }) => {
    await seedStudentAuth(page)
    await page.goto(`${BASE}/institution`)
    await expect(page).not.toHaveURL(/\/institution/)
  })

  test('instructor can open institution shell', async ({ page }) => {
    await seedInstructorAuth(page)
    await page.goto(`${BASE}/institution`)
    await expect(page).toHaveURL(/\/institution/)
    await expect(
      page.getByRole('heading', { name: /Kurum|Risk|ROI|Öğrenci|Genel/i }).first(),
    ).toBeVisible({ timeout: 10000 })
  })

  test('instructor does not see student Sohbet nav', async ({ page }) => {
    await seedInstructorAuth(page)
    await page.setViewportSize({ width: 390, height: 844 })
    await page.goto(`${BASE}/institution`)
    const nav = page.getByRole('navigation', { name: 'Mobil navigasyon' })
    await expect(nav).toBeVisible({ timeout: 10000 })
    await expect(nav.getByText('Sohbet')).toHaveCount(0)
    await expect(nav.getByText('Asistan').or(nav.getByText('Kurum'))).toBeVisible()
  })

  test('instructor blocked from /chat', async ({ page }) => {
    await seedInstructorAuth(page)
    await page.goto(`${BASE}/chat`)
    await expect(page).not.toHaveURL(/\/chat/)
    await expect(page).toHaveURL(/\/institution/)
  })

  test('instructor can open assistant page', async ({ page }) => {
    await seedInstructorAuth(page)
    await page.goto(`${BASE}/institution/assistant`)
    await expect(page).toHaveURL(/\/institution\/assistant/)
    await expect(
      page.getByText(/metrik|sohbet|asistan|ham/i).first(),
    ).toBeVisible({ timeout: 10000 })
  })
})
