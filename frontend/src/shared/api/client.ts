import { getApiBaseUrl } from '@/shared/api/config'
import { ApiClientError } from '@/shared/api/envelope'
import { authHeaders, clearAuth, setAuth, type AuthUser } from '@/shared/auth/storage'

type AuthResponse = {
  access_token: string
  token_type: string
  user: AuthUser
}

function handleUnauthorized(status: number): void {
  if (status === 401) {
    clearAuth()
    if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
      const next = `${window.location.pathname}${window.location.search}`
      window.location.href = `/login?next=${encodeURIComponent(next)}`
    }
  }
}

async function postAuth(path: string, body: unknown): Promise<AuthResponse> {
  const res = await fetch(`${getApiBaseUrl()}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(body),
  })
  const json = await res.json()
  if (!res.ok || !json.success) {
    throw new ApiClientError(json.error?.message ?? 'Auth failed', {
      code: json.error?.code ?? 'AUTH_ERROR',
      status: res.status,
    })
  }
  return json.data as AuthResponse
}

export async function login(input: {
  tenant_slug: string
  email: string
  password: string
}): Promise<AuthUser> {
  const data = await postAuth('/api/v1/auth/login', input)
  setAuth(data.access_token, data.user)
  return data.user
}

export async function register(input: {
  tenant_slug: string
  email: string
  password: string
  full_name: string
  role?: string
}): Promise<AuthUser> {
  const data = await postAuth('/api/v1/auth/register', input)
  setAuth(data.access_token, data.user)
  return data.user
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${getApiBaseUrl()}${path}`, {
    headers: { Accept: 'application/json', ...authHeaders() },
  })
  const json = await res.json().catch(() => ({}))
  if (!res.ok || !json.success) {
    handleUnauthorized(res.status)
    throw new ApiClientError(json.error?.message ?? 'Request failed', {
      code: json.error?.code ?? 'HTTP_ERROR',
      status: res.status,
    })
  }
  return json.data as T
}

export async function apiPatch<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${getApiBaseUrl()}${path}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...authHeaders(),
    },
    body: JSON.stringify(body),
  })
  const json = await res.json().catch(() => ({}))
  if (!res.ok || !json.success) {
    handleUnauthorized(res.status)
    throw new ApiClientError(json.error?.message ?? 'Request failed', {
      code: json.error?.code ?? 'HTTP_ERROR',
      status: res.status,
    })
  }
  return json.data as T
}

export async function apiPostForm<T>(path: string, form: FormData): Promise<T> {
  const res = await fetch(`${getApiBaseUrl()}${path}`, {
    method: 'POST',
    headers: { ...authHeaders() },
    body: form,
  })
  const json = await res.json().catch(() => ({}))
  if (!res.ok || !json.success) {
    handleUnauthorized(res.status)
    throw new ApiClientError(json.error?.message ?? 'Upload failed', {
      code: json.error?.code ?? 'HTTP_ERROR',
      status: res.status,
    })
  }
  return json.data as T
}
