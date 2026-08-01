import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { apiGet } from '@/shared/api/client'
import { queryKeys } from '@/shared/api/query-keys'

type StudentRow = {
  user_id: string
  full_name: string | null
  email: string
  risk_level: string
  rationale: string | null
  capacity_score: number | null
  metrics: Record<string, unknown> | null
  updated_at?: string | null
}

type Roi = {
  prevented_dropouts: number
  protected_revenue: number
  revenue_per_student: number
  active_high_risk: number
  total_students: number
}

const riskColor: Record<string, string> = {
  green: 'bg-emerald-500/15 text-emerald-300',
  yellow: 'bg-amber-500/15 text-amber-300',
  red: 'bg-red-500/15 text-red-300',
  high_risk: 'bg-red-500/15 text-red-300',
}

const riskLabel: Record<string, string> = {
  green: 'Yeşil',
  yellow: 'Sarı',
  red: 'Kırmızı',
  high_risk: 'Kırmızı',
}

function formatTry(amount: number): string {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    maximumFractionDigits: 0,
  }).format(amount)
}

function metricLines(metrics: Record<string, unknown> | null): string[] {
  if (!metrics) return []
  const lines: string[] = []
  if (typeof metrics.missed_checkin === 'boolean') {
    lines.push(
      metrics.missed_checkin
        ? 'Bu hafta check-in kaçırıldı'
        : 'Check-in durumu güncel',
    )
  }
  if (typeof metrics.task_completion_rate === 'number') {
    lines.push(
      `Görev tamamlanma oranı: %${Math.round(metrics.task_completion_rate * 100)}`,
    )
  }
  if (typeof metrics.capacity_score === 'number') {
    lines.push(`Kapasite skoru: ${metrics.capacity_score}`)
  }
  if (typeof metrics.open_tasks === 'number') {
    lines.push(`Açık görev: ${metrics.open_tasks}`)
  }
  if (metrics.source === 'guardrail') {
    lines.push(`Guardrail sinyali: ${String(metrics.category ?? 'risk')}`)
  }
  return lines
}

export function InstitutionPage() {
  const [search, setSearch] = useState('')
  const [riskFilter, setRiskFilter] = useState<'all' | 'red' | 'yellow' | 'green'>(
    'all',
  )
  const [selected, setSelected] = useState<StudentRow | null>(null)

  const studentsQuery = useQuery({
    queryKey: queryKeys.institution.students(),
    queryFn: () =>
      apiGet<{ students: StudentRow[] }>('/api/v1/institution/students'),
  })
  const roiQuery = useQuery({
    queryKey: queryKeys.institution.roi(),
    queryFn: () => apiGet<Roi>('/api/v1/institution/roi'),
  })

  const filtered = useMemo(() => {
    const list = studentsQuery.data?.students ?? []
    const q = search.trim().toLowerCase()
    return list.filter((s) => {
      const level = s.risk_level === 'high_risk' ? 'red' : s.risk_level
      if (riskFilter !== 'all' && level !== riskFilter) return false
      if (!q) return true
      const hay = `${s.full_name ?? ''} ${s.email}`.toLowerCase()
      return hay.includes(q)
    })
  }, [studentsQuery.data?.students, search, riskFilter])

  const students = studentsQuery.data?.students ?? []
  const roi = roiQuery.data ?? null
  const loading = studentsQuery.isLoading || roiQuery.isLoading
  const error =
    studentsQuery.error instanceof Error
      ? studentsQuery.error.message
      : roiQuery.error instanceof Error
        ? roiQuery.error.message
        : null

  if (error) {
    return (
      <div className="p-6">
        <p className="text-sm text-red-300" role="alert">
          {error}
        </p>
        <button
          type="button"
          className="mt-3 text-sm font-medium text-equa-primary underline"
          onClick={() => {
            void studentsQuery.refetch()
            void roiQuery.refetch()
          }}
        >
          Yeniden dene
        </button>
        <Link to="/login" className="mt-2 ml-4 inline-block text-equa-primary underline">
          Giriş yap
        </Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-6">
      <h1 className="font-display text-xl font-semibold text-equa-ink">
        Risk & müdahale
      </h1>
      <p className="mt-1 text-sm text-equa-muted">
        10 saniyede kimler kırmızı, neden, ne yapılmalı.
      </p>

      {loading && !roi ? (
        <div className="mt-6 grid gap-4 sm:grid-cols-3" aria-busy="true">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-16 animate-pulse rounded-xl bg-equa-line/40"
            />
          ))}
        </div>
      ) : roi ? (
        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          <div>
            <p className="text-xs uppercase tracking-wide text-equa-muted">
              Önlenen dropout
            </p>
            <p className="font-display text-2xl font-semibold">
              {roi.prevented_dropouts}
            </p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-equa-muted">
              Korunan gelir
            </p>
            <p className="font-display text-2xl font-semibold">
              {formatTry(roi.protected_revenue)}
            </p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-equa-muted">
              Aktif yüksek risk
            </p>
            <p className="font-display text-2xl font-semibold">
              {roi.active_high_risk}/{roi.total_students}
            </p>
          </div>
        </div>
      ) : null}

      <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-end">
        <div className="flex-1">
          <label htmlFor="student-search" className="text-sm font-medium text-equa-ink">
            Ara
          </label>
          <input
            id="student-search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="İsim veya e-posta"
            className="mt-1 w-full rounded-xl border border-equa-line bg-[#0A0A14] px-3 py-2.5 text-sm"
          />
        </div>
        <div>
          <label htmlFor="risk-filter" className="text-sm font-medium text-equa-ink">
            Risk
          </label>
          <select
            id="risk-filter"
            value={riskFilter}
            onChange={(e) =>
              setRiskFilter(e.target.value as typeof riskFilter)
            }
            className="mt-1 block rounded-xl border border-equa-line bg-[#0A0A14] px-3 py-2.5 text-sm"
          >
            <option value="all">Tümü</option>
            <option value="red">Kırmızı</option>
            <option value="yellow">Sarı</option>
            <option value="green">Yeşil</option>
          </select>
        </div>
      </div>

      {filtered.length === 0 ? (
        <p className="mt-8 text-sm text-equa-muted" role="status">
          {students.length === 0
            ? 'Henüz öğrenci yok veya risk sinyali oluşmamış.'
            : 'Filtreyle eşleşen öğrenci yok.'}
        </p>
      ) : (
        <ul className="mt-6 divide-y divide-equa-line/60 border-t border-equa-line/60">
          {filtered.map((s) => {
            const level = s.risk_level === 'high_risk' ? 'red' : s.risk_level
            return (
              <li
                key={s.user_id}
                className="flex flex-col gap-2 py-4 sm:flex-row sm:items-start sm:justify-between"
              >
                <div className="min-w-0">
                  <p className="font-medium text-equa-ink">
                    {s.full_name || s.email}
                  </p>
                  <p className="text-sm text-equa-muted">{s.email}</p>
                  {s.rationale ? (
                    <p className="mt-1 text-sm text-equa-muted">{s.rationale}</p>
                  ) : null}
                  {level === 'red' ? (
                    <button
                      type="button"
                      onClick={() => setSelected(s)}
                      className="mt-2 text-sm font-medium text-equa-primary underline"
                    >
                      Neden kırmızı?
                    </button>
                  ) : null}
                </div>
                <span
                  className={[
                    'inline-flex w-fit rounded-md px-2.5 py-1 text-xs font-medium uppercase transition-colors duration-300',
                    riskColor[level] ?? 'bg-equa-accent-soft text-equa-ink',
                  ].join(' ')}
                  aria-label={`Risk: ${riskLabel[level] ?? level}`}
                >
                  {riskLabel[level] ?? level}
                </span>
              </li>
            )
          })}
        </ul>
      )}

      {selected ? (
        <div
          className="fixed inset-0 z-50 flex items-end justify-center bg-equa-bg/70 p-4 backdrop-blur-sm sm:items-center"
          role="dialog"
          aria-modal="true"
          aria-labelledby="xai-title"
          onClick={() => setSelected(null)}
        >
          <div
            className="w-full max-w-md rounded-2xl border border-equa-line bg-equa-surface p-5 shadow-lg"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 id="xai-title" className="font-display text-lg font-semibold">
              Neden kırmızı?
            </h2>
            <p className="mt-1 text-sm text-equa-muted">
              {selected.full_name || selected.email} — davranışsal metrikler (ham
              sohbet yok).
            </p>
            <ul className="mt-4 list-disc space-y-1 pl-5 text-sm text-equa-ink">
              {metricLines(selected.metrics).map((line) => (
                <li key={line}>{line}</li>
              ))}
              {selected.rationale ? <li>{selected.rationale}</li> : null}
            </ul>
            {selected.updated_at ? (
              <p className="mt-3 text-xs text-equa-muted">
                Güncellendi: {new Date(selected.updated_at).toLocaleString('tr-TR')}
              </p>
            ) : null}
            <button
              type="button"
              className="mt-5 w-full rounded-xl bg-gradient-to-r from-equa-primary-container to-equa-primary py-2.5 text-sm font-bold text-equa-on-primary"
              onClick={() => setSelected(null)}
            >
              Kapat
            </button>
          </div>
        </div>
      ) : null}
    </div>
  )
}
