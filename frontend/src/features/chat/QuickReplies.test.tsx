import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { QuickReplies } from '@/features/chat/QuickReplies'

describe('QuickReplies', () => {
  it('renders chips and calls onSelect', async () => {
    const user = userEvent.setup()
    const onSelect = vi.fn()
    render(
      <QuickReplies
        replies={['İyiyim', 'Yorgunum']}
        onSelect={onSelect}
      />,
    )

    expect(screen.getByTestId('quick-replies')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'İyiyim' }))
    expect(onSelect).toHaveBeenCalledWith('İyiyim')
  })

  it('renders nothing when empty', () => {
    const { container } = render(
      <QuickReplies replies={[]} onSelect={() => undefined} />,
    )
    expect(container).toBeEmptyDOMElement()
  })
})
