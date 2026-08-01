import { getApiBaseUrl } from './config'
import { ApiClientError } from './envelope'
import { parseSse, type ChatSseEvent } from './sse'
import { authHeaders } from '@/shared/auth/storage'

/**
 * POST /api/v1/institution/assistant/stream — staff metrics assistant SSE.
 */
export async function* streamInstitutionAssistant(
  message: string,
): AsyncGenerator<ChatSseEvent> {
  const url = `${getApiBaseUrl()}/api/v1/institution/assistant/stream`

  let response: Response
  try {
    response = await fetch(url, {
      method: 'POST',
      headers: {
        Accept: 'text/event-stream',
        'Content-Type': 'application/json',
        ...authHeaders(),
      },
      body: JSON.stringify({ message }),
    })
  } catch (err) {
    throw new ApiClientError('Ağ bağlantısı kurulamadı.', {
      code: 'NETWORK_ERROR',
      status: 0,
      details: [err instanceof Error ? err.message : String(err)],
    })
  }

  if (!response.ok) {
    let messageText = 'Asistan isteği başarısız oldu.'
    let code = 'HTTP_ERROR'
    try {
      const json = (await response.json()) as {
        error?: { message?: string; code?: string }
      }
      messageText = json.error?.message ?? messageText
      code = json.error?.code ?? code
    } catch {
      // ignore non-JSON error bodies
    }
    throw new ApiClientError(messageText, { code, status: response.status })
  }

  if (!response.body) {
    throw new ApiClientError('Boş stream yanıtı.', {
      code: 'EMPTY_STREAM',
      status: response.status,
    })
  }

  yield* parseSse(response.body)
}
