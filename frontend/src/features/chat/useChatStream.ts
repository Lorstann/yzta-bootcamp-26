import { useCallback, useRef, useState } from 'react'
import { streamChat } from '@/shared/api/chat'
import { ApiClientError } from '@/shared/api/envelope'
import { getStoredUser } from '@/shared/auth/storage'
import type { ChatMessage, ChatStatus } from './types'

const DEMO_TENANT_ID = '11111111-1111-1111-1111-111111111111'
const DEMO_SESSION_ID = '00000000-0000-4000-8000-000000000010'

function createId(): string {
  return crypto.randomUUID()
}

export function useChatStream(sessionId?: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [status, setStatus] = useState<ChatStatus>('idle')
  const [error, setError] = useState<string | null>(null)
  const [weeklyTasks, setWeeklyTasks] = useState<string[] | null>(null)
  const lastUserMessageRef = useRef<string>('')

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim()
      if (!trimmed || status === 'streaming') return

      lastUserMessageRef.current = trimmed
      setError(null)
      setWeeklyTasks(null)
      setStatus('streaming')

      const user = getStoredUser()
      const tenantId = user?.tenant_id ?? DEMO_TENANT_ID
      const sid = sessionId ?? DEMO_SESSION_ID

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
          tenant_id: tenantId,
          session_id: sid,
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
            if (event.weekly_tasks?.length) {
              setWeeklyTasks(event.weekly_tasks)
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

  return {
    messages,
    status,
    error,
    weeklyTasks,
    sendMessage,
    retry,
  }
}
