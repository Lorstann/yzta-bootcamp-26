import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Check, Sparkles } from 'lucide-react'
import { apiGet, apiPatch } from '@/shared/api/client'
import { ApiClientError } from '@/shared/api/envelope'
import { queryKeys } from '@/shared/api/query-keys'
import {
  Badge,
  Card,
  EmptyState,
  GlassPanel,
  ProgressRing,
  Skeleton,
} from '@/components/ui'

type Task = {
  id: string
  title: string
  description?: string | null
  is_completed: boolean
  status?: string
  checkin_date?: string | null
  due_date?: string | null
}

function tasksErrorMessage(error: unknown): string {
  if (error instanceof ApiClientError) {
    const raw = error.message.trim()
    if (!raw || /^not\s*found$/i.test(raw) || error.status === 404) {
      return 'Bugünün görevleri bulunamadı. Lütfen tekrar dene.'
    }
    return raw
  }
  if (error instanceof Error && error.message) {
    if (/^not\s*found$/i.test(error.message.trim())) {
      return 'Bugünün görevleri bulunamadı. Lütfen tekrar dene.'
    }
    return error.message
  }
  return 'Görevler yüklenemedi. Lütfen tekrar dene.'
}

export function TasksPage() {
  const queryClient = useQueryClient()
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: queryKeys.tasks.all(),
    queryFn: () => apiGet<{ tasks: Task[] }>('/api/v1/tasks'),
  })

  const toggleMutation = useMutation({
    mutationFn: (task: Task) =>
      apiPatch<Task>(`/api/v1/tasks/${task.id}`, {
        is_completed: !task.is_completed,
      }),
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.tasks.all() })
      void queryClient.invalidateQueries({ queryKey: queryKeys.checkin.current() })
    },
  })

  const tasks = data?.tasks ?? []
  const done = tasks.filter((t) => t.is_completed).length
  const total = tasks.length
  const pct = total ? Math.round((done / total) * 100) : 0

  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl space-y-4 px-4 py-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-40 w-full" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <p className="text-sm text-red-300" role="alert">
          {tasksErrorMessage(error)}
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

  return (
    <div className="mx-auto max-w-3xl space-y-6 px-4 py-6 lg:px-8">
      <div>
        <h1 className="font-display text-2xl font-extrabold text-equa-ink lg:text-3xl">
          Bugünün Hedefleri
        </h1>
        <p className="mt-1 flex items-center gap-1 text-sm text-equa-muted">
          <Sparkles size={14} className="text-equa-tertiary" aria-hidden />
          AI tarafından müfredata göre oluşturuldu.
        </p>
      </div>

      <GlassPanel className="flex flex-col items-center gap-4 p-6 sm:flex-row sm:justify-between">
        <ProgressRing value={pct} label={`${done} / ${total || 0} tamamlandı`} size={120} />
        <p className="text-center text-sm text-equa-muted sm:text-left">
          {pct >= 66 ? 'Harika ilerleme!' : 'Küçük adımlarla devam.'}
        </p>
      </GlassPanel>

      {tasks.length === 0 ? (
        <EmptyState
          title="Henüz görev yok"
          description="Sohbette check-in'i tamamla — görevler burada listelenir."
        />
      ) : (
        <ul className="space-y-4">
          {tasks.map((task) => (
            <li key={task.id}>
              <Card
                className={[
                  'p-5 transition-all hover:border-equa-primary/40',
                  task.is_completed ? 'opacity-60' : '',
                  task.status === 'suspended' ? 'border-l-4 border-l-equa-error' : '',
                ].join(' ')}
              >
                <button
                  type="button"
                  className="flex w-full items-start gap-3 text-left"
                  onClick={() => toggleMutation.mutate(task)}
                  disabled={toggleMutation.isPending}
                >
                  <span
                    className={[
                      'mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded border-2',
                      task.is_completed
                        ? 'border-equa-primary bg-equa-primary'
                        : 'border-equa-outline',
                    ].join(' ')}
                  >
                    {task.is_completed ? (
                      <Check size={12} className="text-equa-on-primary" />
                    ) : null}
                  </span>
                  <span className="min-w-0 flex-1">
                    <span
                      className={[
                        'block font-bold text-equa-ink',
                        task.is_completed ? 'line-through' : '',
                      ].join(' ')}
                    >
                      {task.title}
                    </span>
                    {task.description ? (
                      <span className="mt-1 block text-sm text-equa-muted">
                        {task.description}
                      </span>
                    ) : null}
                    <span className="mt-2 flex flex-wrap gap-2">
                      {task.status === 'suspended' ? (
                        <Badge tone="yellow">Askıda</Badge>
                      ) : null}
                      {task.checkin_date ? (
                        <Badge tone="neutral">{task.checkin_date}</Badge>
                      ) : null}
                    </span>
                  </span>
                </button>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
