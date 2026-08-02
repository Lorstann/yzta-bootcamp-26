import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { apiGet } from '@/shared/api/client'
import { queryKeys } from '@/shared/api/query-keys'
import emptyCalendar from '@/assets/empty/calendar.png'
import { Badge, Button, GlassPanel, Skeleton } from '@/components/ui'

type HistorySession = {
  id: string
  checkin_date: string
  status: string
  summary: string | null
  mood_score: number | null
  task_count: number
  completed_task_count: number
}

type Task = {
  id: string
  title: string
  is_completed: boolean
  due_date?: string | null
  checkin_date?: string | null
  completed_at?: string | null
  status?: string
}

const WEEKDAYS = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']

function daysInMonth(year: number, month: number) {
  return new Date(year, month + 1, 0).getDate()
}

function startWeekday(year: number, month: number) {
  const d = new Date(year, month, 1).getDay()
  return d === 0 ? 6 : d - 1
}

export function CalendarPage() {
  const today = new Date()
  const [cursor, setCursor] = useState(
    () => new Date(today.getFullYear(), today.getMonth(), 1),
  )
  const [selected, setSelected] = useState(
    () => today.toISOString().slice(0, 10),
  )

  const { data: history, isLoading: histLoading } = useQuery({
    queryKey: queryKeys.checkin.history(),
    queryFn: () =>
      apiGet<{ sessions: HistorySession[] }>('/api/v1/checkins/history?limit=365'),
  })
  const { data: taskData, isLoading: taskLoading } = useQuery({
    queryKey: queryKeys.tasks.all(),
    queryFn: () => apiGet<{ tasks: Task[] }>('/api/v1/tasks'),
  })

  const year = cursor.getFullYear()
  const month = cursor.getMonth()
  const dim = daysInMonth(year, month)
  const offset = startWeekday(year, month)

  const eventsByDay = useMemo(() => {
    const map = new Map<string, { label: string; tone: 'accent' | 'cyan' | 'yellow' }[]>()
    for (const s of history?.sessions ?? []) {
      const key = s.checkin_date
      const list = map.get(key) ?? []
      list.push({ label: 'Check-in', tone: 'accent' })
      map.set(key, list)
    }
    for (const t of taskData?.tasks ?? []) {
      const key = t.due_date || t.completed_at?.slice(0, 10) || t.checkin_date
      if (!key) continue
      const list = map.get(key) ?? []
      list.push({
        label: t.title.slice(0, 18),
        tone: t.is_completed ? 'cyan' : 'yellow',
      })
      map.set(key, list)
    }
    return map
  }, [history, taskData])

  const selectedTasks = (taskData?.tasks ?? []).filter((t) => {
    const key = t.due_date || t.completed_at?.slice(0, 10) || t.checkin_date
    return key === selected
  })
  const selectedSession = (history?.sessions ?? []).find(
    (s) => s.checkin_date === selected,
  )

  const monthLabel = cursor.toLocaleDateString('tr-TR', {
    month: 'long',
    year: 'numeric',
  })

  if (histLoading || taskLoading) {
    return (
      <div className="p-6">
        <Skeleton className="h-96 w-full" />
      </div>
    )
  }

  return (
    <div className="flex h-full min-h-0 flex-col gap-6 p-4 lg:flex-row lg:p-8">
      <GlassPanel className="min-w-0 flex-1 p-6">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="font-display text-xl font-bold capitalize text-equa-ink">
            {monthLabel}
          </h1>
          <div className="flex items-center gap-2">
            <Button
              variant="icon"
              aria-label="Önceki ay"
              onClick={() =>
                setCursor(new Date(year, month - 1, 1))
              }
            >
              <ChevronLeft size={20} />
            </Button>
            <Button
              variant="ghost"
              className="!min-h-9 !px-3 !py-1.5 !text-xs"
              onClick={() => {
                const n = new Date()
                setCursor(new Date(n.getFullYear(), n.getMonth(), 1))
                setSelected(n.toISOString().slice(0, 10))
              }}
            >
              Bugün
            </Button>
            <Button
              variant="icon"
              aria-label="Sonraki ay"
              onClick={() =>
                setCursor(new Date(year, month + 1, 1))
              }
            >
              <ChevronRight size={20} />
            </Button>
          </div>
        </div>

        <div
          role="grid"
          aria-label="Günlük takvim"
          className="grid grid-cols-7 gap-1"
        >
          {WEEKDAYS.map((d) => (
            <div
              key={d}
              role="columnheader"
              className="py-2 text-center text-xs font-bold uppercase text-equa-muted"
            >
              {d}
            </div>
          ))}
          {Array.from({ length: offset }).map((_, i) => (
            <div key={`pad-${i}`} className="min-h-16" />
          ))}
          {Array.from({ length: dim }).map((_, i) => {
            const day = i + 1
            const iso = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
            const isSelected = selected === iso
            const isToday = today.toISOString().slice(0, 10) === iso
            const events = eventsByDay.get(iso) ?? []
            return (
              <button
                key={iso}
                type="button"
                role="gridcell"
                aria-selected={isSelected}
                onClick={() => setSelected(iso)}
                className={[
                  'min-h-16 rounded-xl border p-1.5 text-left transition-colors hover:bg-equa-surface-highest/50',
                  isSelected
                    ? 'border-equa-primary bg-equa-primary/10 ring-2 ring-equa-primary'
                    : 'border-transparent',
                  isToday && !isSelected ? 'ring-1 ring-equa-line' : '',
                ].join(' ')}
              >
                <span className="text-sm font-medium text-equa-ink">{day}</span>
                <div className="mt-1 space-y-0.5">
                  {events.slice(0, 2).map((e, idx) => (
                    <span
                      key={`${e.label}-${idx}`}
                      className="block truncate rounded px-1 text-[9px] font-semibold text-equa-primary bg-equa-primary/15"
                    >
                      {e.label}
                    </span>
                  ))}
                </div>
              </button>
            )
          })}
        </div>
      </GlassPanel>

      <GlassPanel className="flex w-full flex-col p-6 lg:w-96">
        <p className="text-[12px] font-bold uppercase tracking-wider text-equa-muted">
          Seçili Gün
        </p>
        <h2 className="mt-1 font-display text-xl font-bold text-equa-ink">
          {new Date(selected + 'T12:00:00').toLocaleDateString('tr-TR', {
            day: 'numeric',
            month: 'long',
            weekday: 'long',
          })}
        </h2>

        <div className="mt-6 flex-1 space-y-3 overflow-y-auto">
          {selectedSession ? (
            <div className="rounded-xl border border-equa-line/20 bg-equa-surface p-3">
              <p className="font-bold text-equa-ink">Günlük check-in</p>
              <p className="mt-1 text-sm text-equa-muted">
                Durum: {selectedSession.status} · {selectedSession.completed_task_count}/
                {selectedSession.task_count} görev
              </p>
            </div>
          ) : null}
          {selectedTasks.length === 0 && !selectedSession ? (
            <div className="flex flex-col items-center py-4 text-center">
              <img
                src={emptyCalendar}
                alt=""
                className="mb-3 h-24 w-auto max-w-[10rem] object-contain"
                decoding="async"
              />
              <p className="text-sm text-equa-muted">Bu günde kayıt yok.</p>
            </div>
          ) : (
            selectedTasks.map((t) => (
              <div
                key={t.id}
                className="rounded-xl border border-equa-line/20 bg-equa-surface p-3"
              >
                <p
                  className={[
                    'font-bold text-equa-ink',
                    t.is_completed ? 'line-through opacity-60' : '',
                  ].join(' ')}
                >
                  {t.title}
                </p>
                <div className="mt-2">
                  {t.is_completed ? (
                    <Badge tone="cyan">Tamamlandı</Badge>
                  ) : t.status === 'suspended' ? (
                    <Badge tone="yellow">Askıda</Badge>
                  ) : (
                    <Badge tone="accent">Açık</Badge>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </GlassPanel>
    </div>
  )
}
