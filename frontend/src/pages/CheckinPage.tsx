import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiGet, apiPatch } from '@/shared/api/client'
import { getAccessToken } from '@/shared/auth/storage'

type Task = {
  id: string
  title: string
  is_completed: boolean
}

type CheckinSession = {
  id: string
  week_start: string
  status: string
  summary: string | null
  messages: { role: string; content: string }[]
  weekly_tasks: Task[]
}

export function CheckinPage() {
  const [session, setSession] = useState<CheckinSession | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!getAccessToken()) {
      setError('Check-in için giriş yapmalısın.')
      setLoading(false)
      return
    }
    void apiGet<CheckinSession>('/api/v1/checkins/current')
      .then(setSession)
      .catch((err) => setError(err instanceof Error ? err.message : 'Hata'))
      .finally(() => setLoading(false))
  }, [])

  async function toggleTask(task: Task) {
    const updated = await apiPatch<Task>(`/api/v1/tasks/${task.id}`, {
      is_completed: !task.is_completed,
    })
    setSession((prev) =>
      prev
        ? {
            ...prev,
            weekly_tasks: prev.weekly_tasks.map((t) =>
              t.id === updated.id
                ? { ...t, is_completed: updated.is_completed }
                : t,
            ),
          }
        : prev,
    )
  }

  if (loading) {
    return <p className="p-6 text-sm text-equa-muted">Yükleniyor…</p>
  }

  if (error) {
    return (
      <div className="p-6">
        <p className="text-sm text-red-700" role="alert">
          {error}
        </p>
        <Link to="/login" className="mt-3 inline-block text-equa-accent underline">
          Giriş yap
        </Link>
      </div>
    )
  }

  if (!session) return null

  return (
    <div className="mx-auto max-w-3xl px-4 py-6">
      <h1 className="font-display text-lg font-semibold text-equa-ink">
        Haftalık check-in
      </h1>
      <p className="mt-1 text-sm text-equa-muted">
        Hafta başlangıcı: {session.week_start} · Durum: {session.status}
      </p>

      <div className="mt-6 space-y-3">
        {(session.messages || []).map((m, i) => (
          <div
            key={`${m.role}-${i}`}
            className={[
              'rounded-2xl px-3.5 py-2.5 text-sm',
              m.role === 'user'
                ? 'ml-8 bg-equa-accent text-white'
                : 'mr-8 border border-equa-line/50 bg-white/80',
            ].join(' ')}
          >
            {m.content}
          </div>
        ))}
      </div>

      {session.weekly_tasks?.length ? (
        <div className="mt-8">
          <h2 className="font-display text-base font-semibold">Görevler</h2>
          <ul className="mt-3 space-y-2">
            {session.weekly_tasks.map((task) => (
              <li key={task.id}>
                <label className="flex items-start gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={task.is_completed}
                    onChange={() => void toggleTask(task)}
                    className="mt-1"
                  />
                  <span
                    className={
                      task.is_completed ? 'text-equa-muted line-through' : ''
                    }
                  >
                    {task.title}
                  </span>
                </label>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="mt-6 text-sm text-equa-muted">
          Henüz görev yok.{' '}
          <Link to="/chat" className="text-equa-accent underline">
            Sohbette check-in’i tamamla
          </Link>
        </p>
      )}
    </div>
  )
}
