/** SSE event shapes for POST /api/v1/chat/stream */

export type CheckinStatePayload = {
  enerji?: number | null
  motivasyon?: number | null
  engel?: string | null
  yuk?: string | null
  hazir?: boolean
}

export type ChatSseChunkEvent = {
  type: 'chunk'
  data: string
}

export type ChatSseDoneEvent = {
  type: 'done'
  guardrail_triggered: boolean
  guardrail_category: 'critical' | 'dropout' | 'depression' | null
  daily_tasks: string[] | null
  checkin_completed?: boolean
  state?: CheckinStatePayload | null
  stage?: string
  turn_count?: number | null
  mode?: 'checkin' | 'coach'
  quick_replies?: string[] | null
}

export type ChatSseErrorEvent = {
  type: 'error'
  message: string
}

export type ChatSseEvent =
  | ChatSseChunkEvent
  | ChatSseDoneEvent
  | ChatSseErrorEvent

function parseEventPayload(raw: string): ChatSseEvent | null {
  const trimmed = raw.trim()
  if (!trimmed) return null

  let parsed: unknown
  try {
    parsed = JSON.parse(trimmed)
  } catch {
    return null
  }

  if (!parsed || typeof parsed !== 'object' || !('type' in parsed)) {
    return null
  }

  const event = parsed as { type: string }
  if (event.type === 'chunk' || event.type === 'done' || event.type === 'error') {
    return parsed as ChatSseEvent
  }

  return null
}

/**
 * Parse an SSE ReadableStream into chat events.
 * Expects lines of the form `data: {...}` separated by blank lines.
 */
export async function* parseSse(
  stream: ReadableStream<Uint8Array>,
): AsyncGenerator<ChatSseEvent> {
  const reader = stream.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const parts = buffer.split('\n\n')
      buffer = parts.pop() ?? ''

      for (const part of parts) {
        for (const line of part.split('\n')) {
          const trimmed = line.trimEnd()
          if (!trimmed.startsWith('data:')) continue
          const payload = trimmed.slice(5).trimStart()
          const event = parseEventPayload(payload)
          if (event) yield event
        }
      }
    }

    if (buffer.trim()) {
      for (const line of buffer.split('\n')) {
        const trimmed = line.trimEnd()
        if (!trimmed.startsWith('data:')) continue
        const payload = trimmed.slice(5).trimStart()
        const event = parseEventPayload(payload)
        if (event) yield event
      }
    }
  } finally {
    reader.releaseLock()
  }
}
