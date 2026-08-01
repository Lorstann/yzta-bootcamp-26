import { useCallback, useRef, useState } from 'react'
import { streamChat } from '@/shared/api/chat'
import { ApiClientError } from '@/shared/api/envelope'
import {
  normalizeDailyTasks,
  type CheckinStatePayload,
  type DailyTaskPayload,
} from '@/shared/api/sse'
import type { ChatMessage, ChatStatus, GuardrailInfo } from './types'

function createId(): string {
  return crypto.randomUUID()
}

/**
 * Streaming chat hook. `sessionId` must be a real check-in session UUID
 * obtained from GET /api/v1/checkins/current.
 */
export function useChatStream(sessionId: string | null) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [status, setStatus] = useState<ChatStatus>('idle')
  const [error, setError] = useState<string | null>(null)
  const [dailyTasks, setDailyTasks] = useState<DailyTaskPayload[] | null>(null)
  const [guardrail, setGuardrail] = useState<GuardrailInfo | null>(null)
  const [checkinCompleted, setCheckinCompleted] = useState(false)
  const [checkinState, setCheckinState] = useState<CheckinStatePayload | null>(
    null,
  )
  const [quickReplies, setQuickReplies] = useState<string[]>([])
  const [chatMode, setChatMode] = useState<'checkin' | 'coach'>('checkin')
  const lastUserMessageRef = useRef<string>('')

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim()
      if (!trimmed || status === 'streaming') return
      if (!sessionId) {
        setError('Check-in oturumu henüz hazır değil. Lütfen sayfayı yenile.')
        setStatus('error')
        return
      }

      lastUserMessageRef.current = trimmed
      setError(null)
      setDailyTasks(null)
      setGuardrail(null)
      setQuickReplies([])
      setStatus('streaming')

      const userMsg: ChatMessage = {
        id: createId(),
        role: 'user',
        content: trimmed,
      }
      const assistantId = createId()
      const assistantMsg: ChatMessage = {
        id: assistantId,
        role: 'assistant',
        content: '',
        streaming: true,
      }

      setMessages((prev) => [...prev, userMsg, assistantMsg])

      try {
        for await (const event of streamChat({
          session_id: sessionId,
          message: trimmed,
        })) {
          if (event.type === 'chunk') {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, content: m.content + event.data }
                  : m,
              ),
            )
          } else if (event.type === 'done') {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId ? { ...m, streaming: false } : m,
              ),
            )
            const normalized = normalizeDailyTasks(event.daily_tasks)
            if (normalized?.length) {
              setDailyTasks(normalized)
            }
            if (event.state) {
              setCheckinState((prev) => ({
                ...(prev ?? {}),
                ...event.state,
              }))
            }
            if (event.checkin_completed) {
              setCheckinCompleted(true)
            }
            if (event.mode === 'coach' || event.mode === 'checkin') {
              setChatMode(event.mode)
            } else if (event.checkin_completed) {
              setChatMode('coach')
            }
            if (event.quick_replies?.length) {
              setQuickReplies(event.quick_replies)
            } else {
              setQuickReplies([])
            }
            if (event.guardrail_triggered) {
              setGuardrail({
                triggered: true,
                category: event.guardrail_category,
              })
            }
            setStatus('idle')
          } else if (event.type === 'error') {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? {
                      ...m,
                      content: m.content || event.message,
                      streaming: false,
                    }
                  : m,
              ),
            )
            setError(event.message)
            setStatus('error')
          }
        }
        setStatus((s) => (s === 'streaming' ? 'idle' : s))
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, streaming: false } : m,
          ),
        )
      } catch (err) {
        const message =
          err instanceof ApiClientError
            ? err.message
            : 'Bir hata oluştu. Lütfen tekrar dene.'
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? { ...m, content: m.content || message, streaming: false }
              : m,
          ),
        )
        setError(message)
        setStatus('error')
      }
    },
    [sessionId, status],
  )

  const retry = useCallback(() => {
    const last = lastUserMessageRef.current
    if (!last) return
    setMessages((prev) => prev.slice(0, -2))
    void sendMessage(last)
  }, [sendMessage])

  const hydrateMessages = useCallback((seed: ChatMessage[]) => {
    setMessages(seed)
  }, [])

  const hydrateQuickReplies = useCallback((replies: string[]) => {
    setQuickReplies(replies)
  }, [])

  const hydrateCompleted = useCallback((completed: boolean) => {
    if (completed) {
      setCheckinCompleted(true)
      setChatMode('coach')
    }
  }, [])

  return {
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
  }
}
