import { useCallback, useRef, useState } from 'react'
import { streamInstitutionAssistant } from '@/shared/api/institution'
import { ApiClientError } from '@/shared/api/envelope'
import type { ChatMessage, ChatStatus } from '@/features/chat/types'

function createId(): string {
  return crypto.randomUUID()
}

/**
 * Slim streaming hook for the institution metrics assistant.
 */
export function useInstitutionAssistantStream() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [status, setStatus] = useState<ChatStatus>('idle')
  const [error, setError] = useState<string | null>(null)
  const lastUserMessageRef = useRef<string>('')

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim()
      if (!trimmed || status === 'streaming') return

      lastUserMessageRef.current = trimmed
      setError(null)
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
        for await (const event of streamInstitutionAssistant(trimmed)) {
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
    [status],
  )

  const retry = useCallback(() => {
    const last = lastUserMessageRef.current
    if (!last) return
    setMessages((prev) => prev.slice(0, -2))
    void sendMessage(last)
  }, [sendMessage])

  return { messages, status, error, sendMessage, retry }
}
