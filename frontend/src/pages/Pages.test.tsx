import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it } from 'vitest'
import type { ReactNode } from 'react'
import { LoginPage } from '@/pages/LoginPage'
import { InstitutionPage } from '@/pages/InstitutionPage'
import { CheckinPage } from '@/pages/CheckinPage'
import { setAuth } from '@/shared/auth/storage'

function wrap(ui: ReactNode, route = '/') {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('LoginPage', () => {
  it('shows field validation when email empty', async () => {
    const user = userEvent.setup()
    wrap(<LoginPage />)
    await user.clear(screen.getByLabelText('E-posta'))
    await user.click(screen.getByRole('button', { name: 'Giriş yap' }))
    expect(await screen.findByText(/Geçerli bir e-posta/i)).toBeInTheDocument()
  })
})

describe('InstitutionPage', () => {
  beforeEach(() => {
    setAuth('mock-token', {
      id: '11111111-1111-1111-1111-111111111201',
      tenant_id: '11111111-1111-1111-1111-111111111111',
      email: 'coordinator@equa.dev',
      full_name: 'Coord',
      role: 'instructor',
    })
  })

  it('renders ROI and student risk list with filter', async () => {
    const user = userEvent.setup()
    wrap(<InstitutionPage />)

    expect(await screen.findByText('Risk & müdahale')).toBeInTheDocument()
    expect(await screen.findByText('Ayşe Demir')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Asistan/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Profil/i })).toBeInTheDocument()

    await user.selectOptions(screen.getByLabelText('Risk'), 'red')
    expect(screen.getByText('Ayşe Demir')).toBeInTheDocument()
    expect(screen.queryByText('Mehmet Kaya')).not.toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Neden kırmızı?' }))
    expect(await screen.findByRole('dialog')).toBeInTheDocument()
    expect(screen.getByText(/davranışsal metrikler/i)).toBeInTheDocument()
  })
})

describe('InstitutionProfilePage', () => {
  beforeEach(() => {
    setAuth('mock-token', {
      id: '11111111-1111-1111-1111-111111111201',
      tenant_id: '11111111-1111-1111-1111-111111111111',
      email: 'coordinator@equa.dev',
      full_name: 'Coord',
      role: 'instructor',
    })
  })

  it('shows staff me and usage metrics', async () => {
    const { InstitutionProfilePage } = await import(
      '@/pages/InstitutionProfilePage'
    )
    wrap(<InstitutionProfilePage />)

    expect(await screen.findByText('Kurum Profili')).toBeInTheDocument()
    expect(await screen.findByText('coordinator@equa.dev')).toBeInTheDocument()
    expect(await screen.findByText(/Equa Demo/)).toBeInTheDocument()
    expect(screen.getByText('Adoption (7g)')).toBeInTheDocument()
  })
})

describe('CheckinPage', () => {
  beforeEach(() => {
    setAuth('mock-token', {
      id: '11111111-1111-1111-1111-111111111101',
      tenant_id: '11111111-1111-1111-1111-111111111111',
      email: 'student@equa.dev',
      full_name: 'Student',
      role: 'student',
      onboarding_completed: true,
    })
  })

  it('shows empty tasks CTA to chat', async () => {
    wrap(<CheckinPage />)
    await waitFor(() => {
      expect(screen.getByText(/Henüz görev yok/i)).toBeInTheDocument()
    })
    expect(screen.getByRole('link', { name: /Sohbette/i })).toBeInTheDocument()
  })
})

describe('LandingPage', () => {
  it('renders hero copy', async () => {
    const { LandingPage } = await import('@/pages/LandingPage')
    wrap(<LandingPage />)
    expect(screen.getByText(/Kapasiteni aşmadan ilerle/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /^Başla$/i })).toBeInTheDocument()
  })
})

describe('DashboardPage', () => {
  beforeEach(() => {
    setAuth('mock-token', {
      id: '11111111-1111-1111-1111-111111111101',
      tenant_id: '11111111-1111-1111-1111-111111111111',
      email: 'student@equa.dev',
      full_name: 'Student',
      role: 'student',
      onboarding_completed: true,
    })
  })

  it('renders flow state hero', async () => {
    const { DashboardPage } = await import('@/pages/DashboardPage')
    wrap(<DashboardPage />)
    expect(await screen.findByText('Flow State Aktif')).toBeInTheDocument()
  })
})

describe('TasksPage', () => {
  beforeEach(() => {
    setAuth('mock-token', {
      id: '11111111-1111-1111-1111-111111111101',
      tenant_id: '11111111-1111-1111-1111-111111111111',
      email: 'student@equa.dev',
      full_name: 'Student',
      role: 'student',
      onboarding_completed: true,
    })
  })

  it('lists tasks from API', async () => {
    const { TasksPage } = await import('@/pages/TasksPage')
    wrap(<TasksPage />)
    expect(await screen.findByText('Bugünün Hedefleri')).toBeInTheDocument()
    expect(await screen.findByText(/React Hooks/i)).toBeInTheDocument()
  })
})
