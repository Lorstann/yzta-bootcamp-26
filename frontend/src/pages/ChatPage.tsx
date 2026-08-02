import { useEffect, useRef, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Check } from 'lucide-react'
import { ChatInput } from '@/features/chat/ChatInput'
import { MessageBubble } from '@/features/chat/MessageBubble'
import { QuickReplies } from '@/features/chat/QuickReplies'
import {
  ENERGY_CHOICES,
  MOTIVATION_CHOICES,
  energyLabel,
  motivationLabel,
} from '@/features/chat/scales'
import { useChatStream } from '@/features/chat/useChatStream'
import type { ChatMessage } from '@/features/chat/types'
import { apiGet } from '@/shared/api/client'
import { ApiClientError } from '@/shared/api/envelope'
import emptyChat from '@/assets/empty/chat.png'
import { AiChip, Badge, GlassPanel } from '@/components/ui'

const OPENING_CHIPS = ENERGY_CHOICES.map((c) => c.label)
const EXPLORE_CHIPS = [
  'Zaman yetmiyor',
  'Konuyu anlamadım',
  'Motivasyonum düşük',
  'Mülakat stresi',
  'Başka bir şey',
]

function fallbackChips(session: {
  status: string
  energy_level?: number | null
  motivation_level?: number | null
  stage?: string
  quick_replies?: string[] | null
}): string[] {
  if (session.status === 'completed') return []
  if (session.quick_replies?.length) return session.quick_replies
  if (session.energy_level == null) return [...OPENING_CHIPS]
  if (session.motivation_level == null) {
    return MOTIVATION_CHOICES.map((c) => c.label)
  }
  if ((session.stage ?? 'opening') === 'explore') return [...EXPLORE_CHIPS]
  return []
}

type CheckinSession = {
  id: string
  checkin_date: string
  status: string
  energy_level?: number | null
  motivation_level?: number | null
  stage?: string
  quick_replies?: string[] | null
  messages: Array<{ role: string; content: string }>
  daily_tasks: Array<{
    id: string
    title: string
    is_completed: boolean
  }>
}

export function ChatPage() {
  const location = useLocation()
  const prefill =
    (location.state as { prefill?: string } | null)?.prefill ?? undefined
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [sessionLoading, setSessionLoading] = useState(true)
  const [sessionError, setSessionError] = useState<string | null>(null)
  const [seedEnergy, setSeedEnergy] = useState<number | null>(null)
  const [seedMotivation, setSeedMotivation] = useState<number | null>(null)
  const [sessionStatus, setSessionStatus] = useState<string>('in_progress')
  const {
    messages,
    status,
    error,
    dailyTasks,
    guardrail,
    checkinCompleted,
    checkinState,
    quickReplies,
    chatMode,
    sendMessage,
    retry,
    hydrateMessages,
    hydrateQuickReplies,
    hydrateCompleted,
  } = useChatStream(sessionId)
  const listRef = useRef<HTMLDivElement>(null)
  const isStreaming = status === 'streaming'
  const hydratedRef = useRef(false)
  const prefillSent = useRef(false)

  useEffect(() => {
    let cancelled = false
    setSessionLoading(true)
    setSessionError(null)

    apiGet<CheckinSession>('/api/v1/checkins/current')
      .then((session) => {
        if (cancelled) return
        setSessionId(session.id)
        setSessionStatus(session.status)
        if (session.energy_level != null) setSeedEnergy(session.energy_level)
        if (session.motivation_level != null)
          setSeedMotivation(session.motivation_level)
        if (!hydratedRef.current && session.messages?.length) {
          const seed: ChatMessage[] = session.messages.map((m, i) => ({
            id: `seed-${i}`,
            role: m.role === 'user' ? 'user' : 'assistant',
            content: m.content,
          }))
          hydrateMessages(seed)
          hydratedRef.current = true
        }
        if (session.status === 'completed') {
          hydrateCompleted(true)
        } else {
          const chips = fallbackChips(session)
          if (chips.length) hydrateQuickReplies(chips)
        }
      })
      .catch((err: unknown) => {
        if (cancelled) return
        const message =
          err instanceof ApiClientError
            ? err.message
            : 'Check-in oturumu açılamadı.'
        setSessionError(message)
      })
      .finally(() => {
        if (!cancelled) setSessionLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [hydrateMessages, hydrateQuickReplies, hydrateCompleted])

  useEffect(() => {
    if (!sessionId || !prefill || prefillSent.current || isStreaming) return
    prefillSent.current = true
    void sendMessage(prefill)
  }, [sessionId, prefill, isStreaming, sendMessage])

  useEffect(() => {
    const el = listRef.current
    if (!el) return
    el.scrollTop = el.scrollHeight
  }, [messages, isStreaming, quickReplies])

  if (sessionLoading) {
    return (
      <div className="mx-auto flex h-full w-full max-w-3xl items-center justify-center px-4">
        <p className="text-sm text-equa-muted" role="status">
          Sohbet hazırlanıyor…
        </p>
      </div>
    )
  }

  if (sessionError || !sessionId) {
    return (
      <div className="mx-auto flex h-full w-full max-w-3xl flex-col items-center justify-center gap-3 px-4 text-center">
        <p className="text-sm text-equa-ink" role="alert">
          {sessionError ?? 'Check-in oturumu bulunamadı.'}
        </p>
        <a
          href="/login"
          className="text-sm font-medium text-equa-primary underline"
        >
          Giriş yap
        </a>
      </div>
    )
  }

  const sideTasks =
    dailyTasks && dailyTasks.length > 0 ? dailyTasks : null

  const energy =
    checkinState?.enerji ?? seedEnergy
  const motivation =
    checkinState?.motivasyon ?? seedMotivation
  const energyText = energyLabel(energy)
  const motivationText = motivationLabel(motivation)

  const inCoachMode =
    chatMode === 'coach' ||
    checkinCompleted ||
    sessionStatus === 'completed'

  const aiChipLabel =
    status === 'streaming' ? 'AI yazıyor' : status === 'idle' ? 'AI Canlı' : null

  return (
    <div className="flex h-full min-h-0 w-full flex-col gap-4 p-4 lg:flex-row lg:gap-6 lg:p-6">
      <section
        className="glass-panel flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden rounded-2xl shadow-2xl"
        aria-label="Sohbet alanı"
      >
        <div className="flex shrink-0 items-start justify-between gap-3 border-b border-equa-line/20 px-4 py-3 lg:px-6">
          <div className="min-w-0">
            <h1 className="font-display text-lg font-bold text-equa-ink lg:text-xl">
              {inCoachMode ? 'AI Koç' : 'Günlük Check-in'}
            </h1>
            <p className="text-sm text-equa-muted">
              {inCoachMode
                ? 'Takıldığın bir şey varsa sor — teknik veya sosyal.'
                : 'AI koçunla kısa bir check-in yap.'}
            </p>
            {(energyText != null || motivationText != null) && (
              <p
                className="mt-1 text-xs text-equa-muted"
                data-testid="checkin-signals"
              >
                {energyText != null ? `Enerji: ${energyText}` : null}
                {energyText != null && motivationText != null ? ' · ' : null}
                {motivationText != null
                  ? `Motivasyon: ${motivationText}`
                  : null}
              </p>
            )}
          </div>
          {aiChipLabel ? <AiChip>{aiChipLabel}</AiChip> : null}
        </div>

        <div
          ref={listRef}
          className="min-h-0 flex-1 space-y-6 overflow-y-auto px-4 py-6 lg:px-6"
          data-testid="chat-message-slot"
          aria-live="polite"
        >
          {messages.length === 0 ? (
            <div className="flex h-full min-h-[12rem] flex-col items-center justify-center text-center">
              <img
                src={emptyChat}
                alt=""
                className="mb-4 h-28 w-auto max-w-[12rem] object-contain"
                decoding="async"
              />
              <p className="font-display text-base font-medium text-equa-ink">
                Mesaj yazarak başla
              </p>
              <p className="mt-2 max-w-xs text-sm text-equa-muted">
                Bugün nasıl hissediyorsun? Kısa bir mesaj yeterli.
              </p>
            </div>
          ) : (
            messages.map((m) => (
              <MessageBubble key={m.id} message={m} />
            ))
          )}

          {isStreaming ? (
            <div data-testid="chat-loading" role="status" className="flex gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-equa-primary to-equa-primary-container">
                <span className="sr-only">Yanıt yazılıyor…</span>
              </div>
              <div className="flex w-20 items-center gap-1 rounded-2xl rounded-tl-none border border-equa-line/20 bg-equa-surface px-4 py-5">
                <div className="typing-dot h-2 w-2 rounded-full bg-equa-primary/70" />
                <div className="typing-dot h-2 w-2 rounded-full bg-equa-primary/70" />
                <div className="typing-dot h-2 w-2 rounded-full bg-equa-primary/70" />
              </div>
              <span className="sr-only">Yanıt yazılıyor…</span>
            </div>
          ) : null}

          {error ? (
            <div
              className="rounded-xl border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-300"
              role="alert"
              data-testid="chat-error"
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

          {guardrail?.triggered ? (
            <div
              className="rounded-xl border border-equa-line/40 bg-equa-accent-soft px-3 py-2.5 text-sm text-equa-ink"
              role="status"
              data-testid="guardrail-notice"
            >
              <p className="font-medium">Destek yakında</p>
              <p className="mt-1 text-equa-muted">
                Paylaştığın için teşekkürler. Kurumundaki öğrenci destek
                koordinatörüne haber verildi — seni yargılamadan yanındalar.
              </p>
            </div>
          ) : null}

          {checkinCompleted ? (
            <div
              className="rounded-xl border border-equa-primary/40 bg-equa-primary/10 px-3 py-2.5 text-sm text-equa-ink"
              role="status"
              data-testid="checkin-complete"
            >
              <p className="font-medium">Check-in tamam</p>
              <p className="mt-1 text-equa-muted">
                Takıldığın bir şey varsa sormaya devam et. Görev özetini
                Check-in sayfasında da görebilirsin.
              </p>
              <Link
                to="/checkin"
                className="mt-2 inline-block text-sm font-medium text-equa-primary underline"
              >
                Check-in özetine git
              </Link>
            </div>
          ) : null}

          {dailyTasks && dailyTasks.length > 0 ? (
            <div
              className="rounded-xl border border-equa-line/30 bg-equa-surface/80 px-3 py-2.5 lg:hidden"
              data-testid="daily-tasks"
            >
              <p className="text-xs font-medium uppercase tracking-wide text-equa-muted">
                Bugünün görevleri
              </p>
              <ul className="mt-1.5 list-disc space-y-2 pl-4 text-sm text-equa-ink">
                {dailyTasks.map((task) => (
                  <li key={task.title}>
                    <span className="font-medium">{task.title}</span>
                    {task.description ? (
                      <p className="mt-0.5 text-xs text-equa-muted">
                        {task.description}
                      </p>
                    ) : null}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>

        <div
          className="shrink-0 border-t border-equa-line/20 bg-equa-surface-low p-4"
          data-testid="chat-input-slot"
          aria-label="Mesaj yazma alanı"
        >
          {quickReplies.length > 0 ? (
            <div className="mb-3">
              <p className="mb-2 text-xs font-medium text-equa-muted">
                Hızlı cevap
              </p>
              <QuickReplies
                replies={quickReplies}
                disabled={isStreaming}
                onSelect={(label) => void sendMessage(label)}
              />
            </div>
          ) : null}
          <ChatInput
            disabled={isStreaming}
            onSend={sendMessage}
          />
        </div>
      </section>

      <aside className="hidden w-96 shrink-0 flex-col lg:flex">
        <GlassPanel className="flex flex-1 flex-col p-6 shadow-xl">
          <div className="mb-6 flex items-center justify-between">
            <h2 className="font-display text-xl font-bold text-equa-ink">
              Günlük Görevler
            </h2>
            <Badge tone="accent">
              {sideTasks ? `${sideTasks.length} Görev` : '—'}
            </Badge>
          </div>
          {sideTasks ? (
            <ul className="space-y-3" data-testid="daily-tasks-desktop">
              {sideTasks.map((task) => (
                <li
                  key={task.title}
                  className="rounded-xl border border-equa-line/20 bg-equa-surface p-4"
                >
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded border-2 border-equa-primary bg-equa-primary">
                      <Check size={12} className="text-equa-on-primary" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-equa-ink">
                        {task.title}
                      </p>
                      {task.description ? (
                        <p className="mt-1 text-xs text-equa-muted">
                          {task.description}
                        </p>
                      ) : null}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-equa-muted">
              Check-in tamamlanınca görevler burada görünür.
            </p>
          )}
        </GlassPanel>
      </aside>
    </div>
  )
}
