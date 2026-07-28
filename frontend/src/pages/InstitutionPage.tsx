import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiGet } from '@/shared/api/client'
import { getAccessToken, getStoredUser } from '@/shared/auth/storage'

type StudentRow = {
  user_id: string
  full_name: string | null
  email: string
  risk_level: string
  rationale: string | null
  capacity_score: number | null
  metrics: Record<string, unknown> | null
}

type Roi = {
  prevented_dropouts: number
  protected_revenue: number
  revenue_per_student: number
  active_high_risk: number
  total_students: number
}

const riskColor: Record<string, string> = {
  green: 'bg-emerald-100 text-emerald-900',
  yellow: 'bg-amber-100 text-amber-900',
  red: 'bg-red-100 text-red-900',
  high_risk: 'bg-red-100 text-red-900',
}

export function InstitutionPage() {
  const [students, setStudents] = useState<StudentRow[]>([])
  const [roi, setRoi] = useState<Roi | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const user = getStoredUser()
    if (!getAccessToken() || !user || !['instructor', 'admin'].includes(user.role)) {
      setError('Kurum paneli için eğitmen/admin girişi gerekli.')
      return
    }
    void Promise.all([
      apiGet<{ students: StudentRow[] }>('/api/v1/institution/students'),
      apiGet<Roi>('/api/v1/institution/roi'),
    ])
      .then(([list, metrics]) => {
        setStudents(list.students)
        setRoi(metrics)
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Hata'))
  }, [])

  if (error) {
    return (
      <div className="p-6">
        <p className="text-sm text-red-700">{error}</p>
        <Link to="/login" className="mt-2 inline-block text-equa-accent underline">
          Giriş yap
        </Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-6">
      <h1 className="font-display text-xl font-semibold text-equa-ink">
        Kurum paneli
      </h1>
      <p className="mt-1 text-sm text-equa-muted">
        Öğrenci risk sinyalleri ve ROI
      </p>

      {roi ? (
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
              ₺{roi.protected_revenue.toLocaleString('tr-TR')}
            </p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-equa-muted">
              Aktif risk
            </p>
            <p className="font-display text-2xl font-semibold">
              {roi.active_high_risk}/{roi.total_students}
            </p>
          </div>
        </div>
      ) : (
        <p className="mt-6 text-sm text-equa-muted">Yükleniyor…</p>
      )}

      <ul className="mt-8 divide-y divide-equa-line/60 border-t border-equa-line/60">
        {students.map((s) => (
          <li key={s.user_id} className="flex flex-col gap-1 py-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="font-medium text-equa-ink">
                {s.full_name || s.email}
              </p>
              <p className="text-sm text-equa-muted">{s.email}</p>
              {s.rationale ? (
                <p className="mt-1 text-sm text-equa-muted">{s.rationale}</p>
              ) : null}
            </div>
            <span
              className={[
                'inline-flex w-fit rounded-md px-2.5 py-1 text-xs font-medium uppercase',
                riskColor[s.risk_level] ?? 'bg-equa-accent-soft text-equa-ink',
              ].join(' ')}
            >
              {s.risk_level}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
