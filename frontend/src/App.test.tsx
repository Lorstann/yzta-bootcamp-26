import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach } from 'vitest'
import App from '@/App'
import { clearAuth, setAuth } from '@/shared/auth/storage'

function seedAuth() {
  setAuth('mock-token', {
    id: '11111111-1111-1111-1111-111111111101',
    tenant_id: '11111111-1111-1111-1111-111111111111',
    email: 'student@example.com',
    full_name: 'Test Student',
    role: 'student',
    onboarding_completed: true,
  })
}

function renderApp(path: string) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[path]}>
        <App />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('App shell', () => {
  beforeEach(() => {
    seedAuth()
  })

  it('renders Equa brand and Sohbet navigation on chat route', async () => {
    renderApp('/chat')

    expect(screen.getAllByText('Equa').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Sohbet').length).toBeGreaterThan(0)
    expect(await screen.findByText('Mesaj yazarak başla')).toBeInTheDocument()
  })

  it('redirects authenticated index to dashboard', async () => {
    renderApp('/')

    expect(await screen.findByText('Flow State Aktif')).toBeInTheDocument()
  })

  it('shows landing for unauthenticated index', async () => {
    clearAuth()
    renderApp('/')

    expect(
      await screen.findByText(/hep yanında/i),
    ).toBeInTheDocument()
  })
})
