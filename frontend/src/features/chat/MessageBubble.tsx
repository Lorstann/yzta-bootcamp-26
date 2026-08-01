import { Bot } from 'lucide-react'
import type { ChatMessage } from './types'
import { AiChip, Avatar } from '@/components/ui'

type MessageBubbleProps = {
  message: ChatMessage
  showAiChip?: boolean
}

export function MessageBubble({ message, showAiChip }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div
      className={[
        'flex w-full gap-3',
        isUser ? 'flex-row-reverse justify-start' : 'justify-start',
      ].join(' ')}
      data-testid={`message-${message.role}`}
    >
      {isUser ? (
        <Avatar alt="Sen" fallback="S" size="sm" />
      ) : (
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-equa-primary to-equa-primary-container shadow-lg shadow-equa-primary/20">
          <Bot size={20} className="text-equa-on-primary" aria-hidden />
        </div>
      )}
      <div
        className={[
          'max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap animate-[fadeSlide_240ms_ease-out]',
          isUser
            ? 'rounded-tr-none border border-equa-primary/30 bg-equa-primary/20 text-equa-ink'
            : 'rounded-tl-none border border-equa-line/20 bg-equa-surface text-equa-ink',
        ].join(' ')}
        role="article"
        aria-label={isUser ? 'Senin mesajın' : 'AI yanıtı'}
      >
        {message.content || (message.streaming ? '…' : '')}
        {message.streaming && message.content ? (
          <span
            className="ml-0.5 inline-block h-3.5 w-1 animate-pulse bg-equa-primary/60 align-middle"
            aria-hidden="true"
          />
        ) : null}
        {showAiChip && !isUser && !message.streaming ? (
          <div className="mt-3">
            <AiChip />
          </div>
        ) : null}
      </div>
    </div>
  )
}
