import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import App from '@/App'

describe('App shell', () => {
  it('renders Equa brand and Sohbet navigation on chat route', () => {
    render(
      <MemoryRouter initialEntries={['/chat']}>
        <App />
      </MemoryRouter>,
    )

    expect(screen.getAllByText('Equa').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Sohbet').length).toBeGreaterThan(0)
    expect(screen.getByText('Mesaj yazarak başla')).toBeInTheDocument()
  })

  it('redirects index to chat content', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>,
    )

    expect(screen.getByText('Mesaj yazarak başla')).toBeInTheDocument()
  })
})
