import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { apiGet, apiPatch } from '@/shared/api/client'
import { queryKeys } from '@/shared/api/query-keys'
import { Badge, Card, ProgressRing } from '@/components/ui'

type Task = {
  id: string
  title: string
  is_completed: boolean
  status?: 'active' | 'suspended'
}

type CheckinSession = {
  id: string
  week_start: string
  status: string
  summary: string | null
  mood_score?: number | null
  messages: { role: string; content: string }[]
  weekly_tasks: Task[]
}

export function CheckinPage() {
  const queryClient = useQueryClient()
  const { data: session, isLoading, error, refetch } = useQuery({
    queryKey: queryKeys.checkin.current(),
    queryFn: () => apiGet<CheckinSession>('/api/v1/checkins/current'),
  })

  const toggleMutation = useMutation({
    mutationFn: (task: Task) =>
      apiPatch<Task>(`/api/v1/tasks/${task.id}`, {
        is_completed: !task.is_completed,
      }),
    onMutate: async (task) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.checkin.current() })
      const prev = queryClient.getQueryData<CheckinSession>(
        queryKeys.checkin.current(),
      )
      if (prev) {
        queryClient.setQueryData<CheckinSession>(queryKeys.checkin.current(), {
          ...prev,
          weekly_tasks: prev.weekly_tasks.map((t) =>
            t.id === task.id ? { ...t, is_completed: !t.is_completed } : t,
          ),
        })
      }
      return { prev }
    },
    onError: (_err, _task, ctx) => {
      if (ctx?.prev) {
        queryClient.setQueryData(queryKeys.checkin.current(), ctx.prev)
      }
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.checkin.current() })
    },
  })

  if (isLoading) {
    return <p className="p-6 text-sm text-equa-muted">Yükleniyor…</p>
  }

  if (error) {
    return (
      <div className="p-6">
        <p className="text-sm text-red-300" role="alert">
          {error instanceof Error ? error.message : 'Hata'}
        </p>
        <button
          type="button"
          onClick={() => void refetch()}
          className="mt-3 text-sm font-medium text-equa-primary underline"
        >
          Yeniden dene
        </button>
      </div>
    )
  }

  if (!session) return null

  const hasSuspended = session.weekly_tasks?.some((t) => t.status === 'suspended')
  const done = session.weekly_tasks?.filter((t) => t.is_completed).length ?? 0
  const total = session.weekly_tasks?.length ?? 0
  const pct = total ? Math.round((done / total) * 100) : 0

  return (
    <div className="mx-auto max-w-3xl space-y-6 px-4 py-6">
      <div>
        <h1 className="font-display text-lg font-semibold text-equa-ink lg:text-xl">
          Haftalık check-in
        </h1>
        <p className="mt-1 text-sm text-equa-muted">
          Hafta başlangıcı: {session.week_start} · Durum: {session.status}
        </p>
      </div>

      {total > 0 ? (
        <Card className="flex items-center gap-6 p-6">
          <ProgressRing value={pct} label={`${done}/${total}`} size={100} />
          <p className="text-sm text-equa-muted">Bu haftanın görev ilerlemesi</p>
        </Card>
      ) : null}

      {hasSuspended ? (
        <p
          className="rounded-xl border border-amber-500/30 bg-amber-500/10 px-3 py-2 text-sm text-amber-200"
          role="status"
        >
          Bu hafta yükünü azalttım — bazı görevler askıya alındı. Kapasiten
          yükseldikçe yeniden açabiliriz.
        </p>
      ) : null}

      <div className="space-y-3">
        {(session.messages || []).length === 0 ? (
          <p className="text-sm text-equa-muted">
            Bu hafta henüz check-in yok.{' '}
            <Link to="/chat" className="text-equa-primary underline">
              Sohbete git
            </Link>
          </p>
        ) : (
          session.messages.map((m, i) => (
            <div
              key={`${m.role}-${i}`}
              className={[
                'rounded-2xl px-3.5 py-2.5 text-sm animate-[fadeSlide_240ms_ease-out]',
                m.role === 'user'
                  ? 'ml-8 border border-equa-primary/30 bg-equa-primary/20 text-equa-ink'
                  : 'mr-8 border border-equa-line/30 bg-equa-surface text-equa-ink',
              ].join(' ')}
            >
              {m.content}
            </div>
          ))
        )}
      </div>

      {session.weekly_tasks?.length ? (
        <div>
          <h2 className="font-display text-base font-semibold text-equa-ink">
            Görevler
          </h2>
          <ul className="mt-3 space-y-2">
            {session.weekly_tasks.map((task) => (
              <li key={task.id}>
                <label className="flex min-h-11 items-start gap-2 rounded-xl border border-equa-line/20 bg-equa-surface/50 px-3 py-3 text-sm">
                  <input
                    type="checkbox"
                    checked={task.is_completed}
                    disabled={
                      task.status === 'suspended' || toggleMutation.isPending
                    }
                    onChange={() => toggleMutation.mutate(task)}
                    className="mt-1 accent-equa-primary"
                  />
                  <span
                    className={
                      task.is_completed ? 'text-equa-muted line-through' : 'text-equa-ink'
                    }
                  >
                    {task.title}
                    {task.status === 'suspended' ? (
                      <Badge tone="yellow" className="ml-2 normal-case">
                        askıya alındı
                      </Badge>
                    ) : null}
                  </span>
                </label>
              </li>
            ))}
          </ul>
          {toggleMutation.isError ? (
            <p className="mt-2 text-sm text-red-300" role="alert">
              Görev güncellenemedi. Tekrar dene.
            </p>
          ) : null}
        </div>
      ) : (
        <p className="text-sm text-equa-muted">
          Henüz görev yok.{' '}
          <Link to="/chat" className="text-equa-primary underline">
            Sohbette check-in’i tamamla
          </Link>
        </p>
      )}
    </div>
  )
}
