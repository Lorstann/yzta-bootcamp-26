import { useEffect, useRef } from 'react'
import { ChatInput } from '@/features/chat/ChatInput'
import { MessageBubble } from '@/features/chat/MessageBubble'
import { useChatStream } from '@/features/chat/useChatStream'

export function ChatPage() {
  const { messages, status, error, weeklyTasks, sendMessage, retry } =
    useChatStream()
  const listRef = useRef<HTMLDivElement>(null)
  const isStreaming = status === 'streaming'

  useEffect(() => {
    const el = listRef.current
    if (!el) return
    el.scrollTop = el.scrollHeight
  }, [messages, isStreaming])

  return (
    <div className="mx-auto flex h-full min-h-0 w-full max-w-3xl flex-col px-4 py-4 lg:max-w-4xl lg:px-8 lg:py-6">
      <div className="mb-3 shrink-0 lg:mb-4">
        <h1 className="font-display text-lg font-semibold text-equa-ink lg:text-xl">
          Sohbet
        </h1>
        <p className="mt-0.5 text-sm text-equa-muted">
          AI koçunla kısa bir check-in yap.
        </p>
      </div>

      <section
        className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden rounded-2xl border border-equa-line/70 bg-equa-surface/60"
        aria-label="Sohbet alanı"
      >
        <div
          ref={listRef}
          className="min-h-0 flex-1 space-y-3 overflow-y-auto px-4 py-6"
          data-testid="chat-message-slot"
          aria-live="polite"
        >
          {messages.length === 0 ? (
            <div className="flex h-full min-h-[12rem] flex-col items-center justify-center text-center">
              <p className="font-display text-base font-medium text-equa-ink">
                Mesaj yazarak başla
              </p>
              <p className="mt-2 max-w-xs text-sm text-equa-muted">
                Bu hafta nasıl hissediyorsun? Kısa bir mesaj yeterli.
              </p>
            </div>
          ) : (
            messages.map((m) => <MessageBubble key={m.id} message={m} />)
          )}

          {isStreaming ? (
            <p
              className="text-xs text-equa-muted"
              data-testid="chat-loading"
              role="status"
            >
              Yanıt yazılıyor…
            </p>
          ) : null}

          {error ? (
            <div
              className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800"
              role="alert"
              data-testid="chat-error"
            >
              <p>{error}</p>
              <button
                type="button"
                onClick={retry}
                className="mt-2 text-sm font-medium text-equa-accent underline"
              >
                Yeniden dene
              </button>
            </div>
          ) : null}

          {weeklyTasks && weeklyTasks.length > 0 ? (
            <div
              className="rounded-xl border border-equa-line/60 bg-white/70 px-3 py-2.5"
              data-testid="weekly-tasks"
            >
              <p className="text-xs font-medium uppercase tracking-wide text-equa-muted">
                Bu haftanın görevleri
              </p>
              <ul className="mt-1.5 list-disc space-y-1 pl-4 text-sm text-equa-ink">
                {weeklyTasks.map((task) => (
                  <li key={task}>{task}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>

        <div
          className="shrink-0 border-t border-equa-line/60 px-3 py-3 lg:px-4"
          data-testid="chat-input-slot"
          aria-label="Mesaj yazma alanı"
        >
          <ChatInput disabled={isStreaming} onSend={sendMessage} />
        </div>
      </section>
    </div>
  )
}
