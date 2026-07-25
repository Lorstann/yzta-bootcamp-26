import { getApiBaseUrl } from './config'
import {
  ApiClientError,
  type ApiEnvelope,
} from './envelope'

export async function fetchJson<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const url = `${getApiBaseUrl()}${path}`

  let response: Response
  try {
    response = await fetch(url, {
      ...init,
      headers: {
        Accept: 'application/json',
        ...(init.body ? { 'Content-Type': 'application/json' } : {}),
        ...init.headers,
      },
    })
  } catch (err) {
    throw new ApiClientError('Ağ bağlantısı kurulamadı.', {
      code: 'NETWORK_ERROR',
      status: 0,
      details: [err instanceof Error ? err.message : String(err)],
    })
  }

  let body: ApiEnvelope<T>
  try {
    body = (await response.json()) as ApiEnvelope<T>
  } catch {
    throw new ApiClientError('Sunucu yanıtı okunamadı.', {
      code: 'INVALID_RESPONSE',
      status: response.status,
    })
  }

  if (!response.ok || body.success === false) {
    const error = body.success === false ? body.error : null
    throw new ApiClientError(error?.message ?? 'İstek başarısız oldu.', {
      code: error?.code ?? 'HTTP_ERROR',
      status: response.status,
      details: error?.details ?? [],
    })
  }

  return body.data
}
