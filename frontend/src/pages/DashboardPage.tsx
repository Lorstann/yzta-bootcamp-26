import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Rocket, Check } from 'lucide-react'
import { apiGet, apiPatch } from '@/shared/api/client'
import { queryKeys } from '@/shared/api/query-keys'
import { MoodSelector } from '@/components/MoodSelector'
import {
  Button,
  Card,
  ProgressBar,
  ProgressRing,
  AiChip,
} from '@/components/ui'

type Task = {
  id: string
  title: string
  is_completed: boolean
  status?: string
}

type CheckinSession = {
  id: string
  checkin_date: string
  status: string
  mood_score: number | null
  daily_tasks: Task[]
}

type Profile = {
  capacity_score: number | null
}

export function DashboardPage() {
  const queryClient = useQueryClient()
  const { data: session } = useQuery({
    queryKey: queryKeys.checkin.current(),
    queryFn: () => apiGet<CheckinSession>('/api/v1/checkins/current'),
  })
  const { data: profile } = useQuery({
    queryKey: queryKeys.profile.me(),
    queryFn: () => apiGet<Profile>('/api/v1/profiles/me'),
  })

  const moodMutation = useMutation({
    mutationFn: (mood_score: number) =>
      apiPatch<CheckinSession>('/api/v1/checkins/current/mood', { mood_score }),
    onMutate: async (mood_score) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.checkin.current() })
      const prev = queryClient.getQueryData<CheckinSession>(
        queryKeys.checkin.current(),
      )
      if (prev) {
        queryClient.setQueryData<CheckinSession>(queryKeys.checkin.current(), {
          ...prev,
          mood_score,
        })
      }
      return { prev }
    },
    onError: (_err, _score, ctx) => {
      if (ctx?.prev) {
        queryClient.setQueryData(queryKeys.checkin.current(), ctx.prev)
      }
    },
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.checkin.current(), data)
    },
  })

  const capacity = profile?.capacity_score ?? 75
  const tasks = session?.daily_tasks ?? []
  const done = tasks.filter((t) => t.is_completed).length
  const total = tasks.length || 3
  const progress = total ? Math.round((done / total) * 100) : 0
  const mood = session?.mood_score ?? null
  const moodError = moodMutation.isError
    ? 'Ruh hali kaydedilemedi. Tekrar dene.'
    : null

  return (
    <div className="relative mx-auto flex max-w-5xl flex-col gap-8 px-4 py-6 lg:px-8">
      <section className="relative overflow-hidden rounded-2xl border border-equa-line/20 bg-equa-surface/30 py-10 text-center backdrop-blur-sm">
        <div className="absolute top-0 left-1/2 h-1 w-3/4 -translate-x-1/2 bg-gradient-to-r from-transparent via-equa-primary to-transparent opacity-50" />
        <h1 className="font-display text-3xl font-extrabold text-equa-ink lg:text-5xl">
          Flow State Aktif
        </h1>
        <p className="mx-auto mt-3 max-w-2xl text-equa-muted">
          Bugünün hedeflerine odaklanmak ve AI koçunla performansını
          değerlendirmek için hazırsan başlayalım.
        </p>
        <Link to="/chat" className="mt-8 inline-block no-underline">
          <Button className="!rounded-full !px-10 !py-4 glow-hover">
            <Rocket size={20} aria-hidden />
            Check-in&apos;i Başlat
          </Button>
        </Link>
      </section>

      <section className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <Card className="flex flex-col items-center p-6">
          <p className="w-full text-left text-[12px] font-bold uppercase tracking-wider text-equa-muted">
            Kapasite Skoru
          </p>
          <ProgressRing
            value={Number(capacity)}
            label={capacity >= 70 ? 'Optimal' : capacity >= 40 ? 'Denge' : 'Düşük'}
            className="mt-6"
          />
        </Card>

        <Card className="flex flex-col justify-between p-6">
          <p className="text-[12px] font-bold uppercase tracking-wider text-equa-muted">
            Günlük Ruh Hali
          </p>
          <MoodSelector
            value={mood}
            onSelect={(score) => moodMutation.mutate(score)}
            disabled={moodMutation.isPending}
            error={moodError}
          />
          <div className="flex justify-center">
            <AiChip>{mood ? 'AI Kayıtlı' : 'Seç'}</AiChip>
          </div>
        </Card>

        <Card className="flex flex-col gap-4 p-6">
          <div className="flex items-center justify-between">
            <p className="text-[12px] font-bold uppercase tracking-wider text-equa-muted">
              Tamamlanan Görevler
            </p>
            <p className="font-display text-2xl font-bold text-equa-primary">
              {done}
              <span className="text-base text-equa-muted">/{total}</span>
            </p>
          </div>
          <ProgressBar value={progress} />
          <ul className="mt-2 flex flex-col gap-3">
            {tasks.length === 0 ? (
              <li className="text-sm text-equa-muted">
                Henüz görev yok —{' '}
                <Link to="/chat" className="text-equa-primary underline">
                  sohbete git
                </Link>
              </li>
            ) : (
              tasks.map((t) => (
                <li
                  key={t.id}
                  className={[
                    'flex items-center gap-3 text-sm',
                    t.is_completed ? 'opacity-60' : 'text-equa-ink',
                  ].join(' ')}
                >
                  <div
                    className={[
                      'flex h-5 w-5 items-center justify-center rounded-full border',
                      t.is_completed
                        ? 'border-equa-primary/50 bg-equa-primary/20'
                        : 'border-equa-outline',
                    ].join(' ')}
                  >
                    {t.is_completed ? (
                      <Check size={12} className="text-equa-primary" />
                    ) : null}
                  </div>
                  <span
                    className={t.is_completed ? 'line-through decoration-equa-outline' : ''}
                  >
                    {t.title}
                  </span>
                </li>
              ))
            )}
          </ul>
        </Card>
      </section>
    </div>
  )
}
