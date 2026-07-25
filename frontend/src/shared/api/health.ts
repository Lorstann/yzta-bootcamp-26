import { fetchJson } from './http'

export type HealthData = {
  status: string
}

/** GET /api/v1/health */
export function getHealth(): Promise<HealthData> {
  return fetchJson<HealthData>('/api/v1/health')
}
