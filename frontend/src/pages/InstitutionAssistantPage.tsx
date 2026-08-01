import { useEffect, useRef } from 'react'
import { ChatInput } from '@/features/chat/ChatInput'
import { MessageBubble } from '@/features/chat/MessageBubble'
import { useInstitutionAssistantStream } from '@/features/institution/useInstitutionAssistantStream'
import { AiChip } from '@/components/ui'

export function InstitutionAssistantPage() {
  const { messages, status, error, sendMessage, retry } =
    useInstitutionAssistantStream()
  const listRef = useRef<HTMLDivElement>(null)
  const isStreaming = status === 'streaming'

  useEffect(() => {
    const el = listRef.current
    if (!el) return
    el.scrollTop = el.scrollHeight
  }, [messages, isStreaming])

  const aiChipLabel =
    status === 'streaming' ? 'AI yazıyor' : status === 'idle' ? 'AI Canlı' : null

  return (
    <div className="flex h-full min-h-0 w-full flex-col p-4 lg:p-6">
      <section
        className="glass-panel flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden rounded-2xl shadow-2xl"
        aria-label="Kurum asistanı"
      >
        <div className="flex shrink-0 flex-col gap-2 border-b border-equa-line/20 px-4 py-3 lg:px-6">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <h1 className="font-display text-lg font-bold text-equa-ink lg:text-xl">
                Kurum Asistanı
              </h1>
              <p className="text-sm text-equa-muted">
                Risk ve adoption metriklerine dayalı sorular sor.
              </p>
            </div>
            {aiChipLabel ? <AiChip>{aiChipLabel}</AiChip> : null}
          </div>
          <p
            className="rounded-xl border border-equa-line/30 bg-equa-accent-soft/40 px-3 py-2 text-xs text-equa-muted"
            role="note"
          >
            Ham öğrenci sohbeti paylaşılmaz — yalnızca metrikler.
          </p>
        </div>

        <div
          ref={listRef}
          className="min-h-0 flex-1 space-y-6 overflow-y-auto px-4 py-6 lg:px-6"
          aria-live="polite"
        >
          {messages.length === 0 ? (
            <div className="flex h-full min-h-[12rem] flex-col items-center justify-center text-center">
              <p className="font-display text-base font-medium text-equa-ink">
                Metrik sorusu sorarak başla
              </p>
              <p className="mt-2 max-w-sm text-sm text-equa-muted">
                Örn. “Bu hafta kaç öğrenci check-in yaptı?” veya “Kırmızı risktekiler
                kim?”
              </p>
            </div>
          ) : (
            messages.map((m) => <MessageBubble key={m.id} message={m} />)
          )}

          {isStreaming ? (
            <div role="status" className="flex gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-equa-primary to-equa-primary-container">
                <span className="sr-only">Yanıt yazılıyor…</span>
              </div>
              <div className="flex w-20 items-center gap-1 rounded-2xl rounded-tl-none border border-equa-line/20 bg-equa-surface px-4 py-5">
                <div className="typing-dot h-2 w-2 rounded-full bg-equa-primary/70" />
                <div className="typing-dot h-2 w-2 rounded-full bg-equa-primary/70" />
                <div className="typing-dot h-2 w-2 rounded-full bg-equa-primary/70" />
              </div>
            </div>
          ) : null}

          {error ? (
            <div
              className="rounded-xl border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-300"
              role="alert"
            >
              <p>{error}</p>
              <button
                type="button"
                onClick={retry}
                className="mt-2 text-sm font-medium text-equa-primary underline"
              >
                Yeniden dene
              </button>
            </div>
          ) : null}
        </div>

        <div className="shrink-0 border-t border-equa-line/20 bg-equa-surface-low p-4">
          <ChatInput
            disabled={isStreaming}
            onSend={sendMessage}
          />
        </div>
      </section>
    </div>
  )
}
