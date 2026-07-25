/** Standard Equa API response envelope types. */

export interface ApiErrorBody {
  code: string
  message: string
  details: unknown[]
}

export interface ApiSuccess<T> {
  success: true
  data: T
  error: null
  meta: Record<string, unknown>
}

export interface ApiFailure {
  success: false
  data: null
  error: ApiErrorBody
  meta: Record<string, unknown>
}

export type ApiEnvelope<T> = ApiSuccess<T> | ApiFailure

export class ApiClientError extends Error {
  readonly code: string
  readonly status: number
  readonly details: unknown[]

  constructor(
    message: string,
    options: { code?: string; status?: number; details?: unknown[] } = {},
  ) {
    super(message)
    this.name = 'ApiClientError'
    this.code = options.code ?? 'CLIENT_ERROR'
    this.status = options.status ?? 0
    this.details = options.details ?? []
  }
}
