import { getApiBaseUrl } from './config'
import { ApiClientError } from './envelope'
import { parseSse, type ChatSseEvent } from './sse'

export type ChatStreamRequest = {
  tenant_id: string
  session_id: string
  message: string
}

/**
 * POST /api/v1/chat/stream — yields SSE chat events until the stream ends.
 */
export async function* streamChat(
  body: ChatStreamRequest,
): AsyncGenerator<ChatSseEvent> {
  const url = `${getApiBaseUrl()}/api/v1/chat/stream`

  let response: Response
  try {
    response = await fetch(url, {
      method: 'POST',
      headers: {
        Accept: 'text/event-stream',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
  } catch (err) {
    throw new ApiClientError('Ağ bağlantısı kurulamadı.', {
      code: 'NETWORK_ERROR',
      status: 0,
      details: [err instanceof Error ? err.message : String(err)],
    })
  }

  if (!response.ok) {
    let message = 'Chat isteği başarısız oldu.'
    let code = 'HTTP_ERROR'
    try {
      const json = (await response.json()) as {
        error?: { message?: string; code?: string }
      }
      message = json.error?.message ?? message
      code = json.error?.code ?? code
    } catch {
      // ignore non-JSON error bodies
    }
    throw new ApiClientError(message, { code, status: response.status })
  }

  if (!response.body) {
    throw new ApiClientError('Boş stream yanıtı.', {
      code: 'EMPTY_STREAM',
      status: response.status,
    })
  }

  yield* parseSse(response.body)
}
