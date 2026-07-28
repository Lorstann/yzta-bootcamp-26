import type { ChatMessage } from './types'

type MessageBubbleProps = {
  message: ChatMessage
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div
      className={[
        'flex w-full',
        isUser ? 'justify-end' : 'justify-start',
      ].join(' ')}
      data-testid={`message-${message.role}`}
    >
      <div
        className={[
          'max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed whitespace-pre-wrap',
          isUser
            ? 'bg-equa-accent text-white'
            : 'bg-white/80 text-equa-ink border border-equa-line/50',
        ].join(' ')}
        role="article"
        aria-label={isUser ? 'Senin mesajın' : 'AI yanıtı'}
      >
        {message.content || (message.streaming ? '…' : '')}
        {message.streaming && message.content ? (
          <span
            className="ml-0.5 inline-block h-3.5 w-1 animate-pulse bg-equa-accent/60 align-middle"
            aria-hidden="true"
          />
        ) : null}
      </div>
    </div>
  )
}
