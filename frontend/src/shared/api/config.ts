/** API client configuration from Vite env. */

export function getApiBaseUrl(): string {
  const base = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
  return base.replace(/\/$/, '')
}

export function isMockEnabled(): boolean {
  return import.meta.env.VITE_USE_MOCK === 'true'
}
