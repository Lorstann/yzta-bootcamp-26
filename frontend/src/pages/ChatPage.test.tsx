import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { ChatPage } from '@/pages/ChatPage'

describe('ChatPage', () => {
  it('shows empty state and sends a message with streaming reply', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter>
        <ChatPage />
      </MemoryRouter>,
    )

    expect(screen.getByText('Mesaj yazarak başla')).toBeInTheDocument()

    const input = screen.getByLabelText('Mesajın')
    await user.type(input, 'Bu hafta iyiyim')
    await user.click(screen.getByRole('button', { name: 'Gönder' }))

    expect(await screen.findByText('Bu hafta iyiyim')).toBeInTheDocument()

    await waitFor(
      () => {
        expect(screen.getByTestId('weekly-tasks')).toBeInTheDocument()
      },
      { timeout: 5000 },
    )
  })

  it('shows error state and retry when message is error', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter>
        <ChatPage />
      </MemoryRouter>,
    )

    const input = screen.getByLabelText('Mesajın')
    await user.type(input, 'error')
    await user.click(screen.getByRole('button', { name: 'Gönder' }))

    expect(await screen.findByTestId('chat-error')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Yeniden dene' })).toBeInTheDocument()
  })
})
