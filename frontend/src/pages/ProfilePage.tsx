import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { School } from 'lucide-react'
import { apiGet, apiPatch, apiPostForm } from '@/shared/api/client'
import { queryKeys } from '@/shared/api/query-keys'
import { getAccessToken, getStoredUser, setAuth } from '@/shared/auth/storage'
import {
  Avatar,
  Button,
  Card,
  Input,
  ProgressBar,
  StatCard,
  Toggle,
} from '@/components/ui'
import { clearAuth } from '@/shared/auth/storage'

type Profile = {
  user_id: string
  capacity_score: number | null
  bio: string | null
  competencies: Record<string, unknown> | null
  city: string | null
  district: string | null
  program_track: string | null
  interests: {
    hobbies?: string[]
    recharge?: string[]
    notes?: string[]
  } | null
  onboarding_completed: boolean
}

type ProfileStats = {
  total_checkins: number
  streak_days: number
  completed_tasks: number
  open_tasks: number
  capacity_history: Array<{ score: number; recorded_at: string }>
}

const TRACK_OPTIONS = [
  'Veri Bilimi',
  'Web Geliştirme',
  'Mobil',
  'Siber Güvenlik',
  'UI-UX',
  'Diğer',
]

const HOBBY_OPTIONS = [
  'Yürüyüş',
  'Spor',
  'Müzik',
  'Kitap',
  'Oyun',
  'Yemek',
  'Sinema',
  'Doğa',
  'Kahve',
  'Sosyalleşme',
]

const RECHARGE_OPTIONS = [
  'Doğada olmak',
  'Arkadaşlarla sohbet',
  'Spor yapmak',
  'Müzik dinlemek',
  'Film/dizi',
  'Uyku/mola',
  'Yalnız kalmak',
  'Yürüyüş',
]

const profileSchema = z.object({
  capacity: z.number().min(0, '0–100 arası').max(100, '0–100 arası'),
  bio: z.string().max(2000).optional(),
  city: z.string().max(120).optional(),
  district: z.string().max(120).optional(),
  program_track: z.string().max(200).optional(),
})

type ProfileForm = z.infer<typeof profileSchema>

function skillChips(competencies: Record<string, unknown> | null): string[] {
  if (!competencies) return []
  const skills = competencies.skills
  if (Array.isArray(skills)) {
    return skills.map(String).slice(0, 20)
  }
  return []
}

export function ProfilePage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const fileRef = useRef<HTMLInputElement>(null)
  const [dragOver, setDragOver] = useState(false)
  const [uploadMsg, setUploadMsg] = useState<string | null>(null)
  const [fallbackHint, setFallbackHint] = useState(false)
  const [emailNotif, setEmailNotif] = useState(true)
  const [taskNotif, setTaskNotif] = useState(true)
  const [hobbies, setHobbies] = useState<string[]>([])
  const [recharge, setRecharge] = useState<string[]>([])
  const [customHobby, setCustomHobby] = useState('')
  const user = getStoredUser()

  const { data: profile, isLoading, error, refetch } = useQuery({
    queryKey: queryKeys.profile.me(),
    queryFn: () => apiGet<Profile>('/api/v1/profiles/me'),
  })
  const { data: stats } = useQuery({
    queryKey: queryKeys.profile.stats(),
    queryFn: () => apiGet<ProfileStats>('/api/v1/profiles/me/stats'),
  })

  const form = useForm<ProfileForm>({
    resolver: zodResolver(profileSchema),
    values: {
      capacity: profile?.capacity_score ?? 70,
      bio: profile?.bio ?? '',
      city: profile?.city ?? '',
      district: profile?.district ?? '',
      program_track: profile?.program_track ?? '',
    },
  })

  // Sync chip state when profile loads
  useEffect(() => {
    if (!profile) return
    setHobbies(profile.interests?.hobbies ?? [])
    setRecharge(profile.interests?.recharge ?? [])
  }, [profile])

  const saveMutation = useMutation({
    mutationFn: (values: ProfileForm) =>
      apiPatch<Profile>('/api/v1/profiles/me/onboarding', {
        capacity_score: values.capacity,
        bio: values.bio || null,
        city: values.city || null,
        district: values.district || null,
        program_track: values.program_track || null,
        interests: {
          hobbies,
          recharge,
          notes: profile?.interests?.notes ?? [],
        },
        onboarding_completed: true,
      }),
    onSuccess: (updated) => {
      queryClient.setQueryData(queryKeys.profile.me(), updated)
      setHobbies(updated.interests?.hobbies ?? [])
      setRecharge(updated.interests?.recharge ?? [])
      void queryClient.invalidateQueries({ queryKey: queryKeys.profile.stats() })
      const token = getAccessToken()
      const stored = getStoredUser()
      if (token && stored) {
        setAuth(token, { ...stored, onboarding_completed: true })
      }
    },
  })

  function toggleList(
    list: string[],
    setList: (v: string[]) => void,
    label: string,
  ) {
    setList(
      list.includes(label)
        ? list.filter((x) => x !== label)
        : [...list, label],
    )
  }

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      if (file.size > 10 * 1024 * 1024) {
        throw new Error('Dosya 10 MB sınırını aşıyor.')
      }
      const name = file.name.toLowerCase()
      if (!name.endsWith('.pdf') && !name.endsWith('.txt')) {
        throw new Error('Sadece PDF veya metin dosyası yükleyebilirsin.')
      }
      const formData = new FormData()
      formData.append('file', file)
      return apiPostForm<{
        competencies: Record<string, unknown>
        fallback_required: boolean
      }>('/api/v1/profiles/me/linkedin', formData)
    },
    onSuccess: (result) => {
      setFallbackHint(result.fallback_required)
      setUploadMsg(
        result.fallback_required
          ? 'PDF okunamadı — sohbette eksik bilgileri tamamlayalım.'
          : 'Yetkinlikler çıkarıldı.',
      )
      void queryClient.invalidateQueries({ queryKey: queryKeys.profile.me() })
    },
    onError: (err) => {
      setUploadMsg(err instanceof Error ? err.message : 'Yükleme başarısız')
    },
  })

  function onDrop(e: React.DragEvent) {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files?.[0]
    if (file) uploadMutation.mutate(file)
  }

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

  if (!profile) return null

  const chips = skillChips(profile.competencies)
  const capacity = profile.capacity_score ?? 0
  const history = stats?.capacity_history ?? []
  const maxScore = Math.max(100, ...history.map((h) => h.score), capacity)
  const pathPoints = history.length
    ? history
        .map((h, i) => {
          const x = (i / Math.max(1, history.length - 1)) * 280 + 10
          const y = 90 - (h.score / maxScore) * 70
          return `${x},${y}`
        })
        .join(' ')
    : ''

  return (
    <div className="mx-auto max-w-4xl space-y-6 px-4 py-6 lg:px-8">
      <Card className="relative overflow-hidden p-0">
        <div className="h-24 bg-gradient-to-r from-equa-primary-container via-equa-surface to-equa-tertiary/20" />
        <div className="flex flex-col items-start gap-4 px-6 pb-6 sm:flex-row sm:items-end">
          <Avatar
            alt={user?.email ?? 'Öğrenci'}
            fallback={(user?.email ?? 'Ö').slice(0, 1).toUpperCase()}
            size="lg"
            className="-mt-10 border-4 border-equa-bg"
          />
          <div className="flex-1">
            <h1 className="font-display text-xl font-bold text-equa-ink">
              {user?.email ?? 'Profil'}
            </h1>
            <p className="mt-1 flex items-center gap-1 text-sm text-equa-muted">
              <School size={14} aria-hidden />
              Onboarding: {profile.onboarding_completed ? 'tamam' : 'eksik'}
            </p>
          </div>
        </div>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard
          label="Toplam Check-in"
          value={stats?.total_checkins ?? '—'}
        />
        <StatCard
          label="Tamamlanan Görev"
          value={stats?.completed_tasks ?? '—'}
        />
        <StatCard
          label="Gün Serisi"
          value={
            stats?.streak_days != null ? `${stats.streak_days} gün` : '—'
          }
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="p-6 lg:col-span-2">
          <h2 className="font-display text-base font-bold text-equa-ink">
            Kapasite Skoru Geçmişi
          </h2>
          <div className="mt-4">
            <p className="text-sm font-medium text-equa-ink">Kapasite</p>
            <div
              className="mt-2"
              role="meter"
              aria-valuenow={capacity}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label="Kapasite skoru"
            >
              <ProgressBar value={capacity} />
            </div>
            <p className="mt-1 text-xs text-equa-muted">{capacity}/100</p>
          </div>
          {pathPoints ? (
            <svg
              viewBox="0 0 300 100"
              className="mt-4 h-28 w-full"
              aria-hidden
            >
              <polyline
                fill="none"
                stroke="url(#capGrad)"
                strokeWidth="3"
                points={pathPoints}
              />
              <defs>
                <linearGradient id="capGrad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#cfbcff" />
                  <stop offset="100%" stopColor="#e7c365" />
                </linearGradient>
              </defs>
            </svg>
          ) : (
            <p className="mt-4 text-sm text-equa-muted">
              Kapasite geçmişi henüz yok — kaydettikçe grafik oluşur.
            </p>
          )}
        </Card>

        <Card className="space-y-4 p-6">
          <h2 className="font-display text-base font-bold text-equa-ink">
            Tercihler
          </h2>
          <Toggle
            label="Email Bildirimleri"
            checked={emailNotif}
            onChange={setEmailNotif}
          />
          <Toggle
            label="Yeni Görev Uyarıları"
            checked={taskNotif}
            onChange={setTaskNotif}
          />
          <Button
            variant="danger"
            className="w-full"
            onClick={() => {
              clearAuth()
              window.location.href = '/login'
            }}
          >
            Çıkış Yap
          </Button>
        </Card>
      </div>

      <form
        onSubmit={form.handleSubmit((values) => saveMutation.mutate(values))}
        className="space-y-4"
      >
        <div>
          <label htmlFor="capacity" className="text-sm font-medium text-equa-ink">
            Kapasite skoru (0–100)
          </label>
          <Input
            id="capacity"
            type="number"
            min={0}
            max={100}
            className="mt-1"
            {...form.register('capacity', { valueAsNumber: true })}
          />
          {form.formState.errors.capacity ? (
            <p className="mt-1 text-sm text-red-300" role="alert">
              {form.formState.errors.capacity.message}
            </p>
          ) : null}
        </div>
        <div>
          <label htmlFor="program_track" className="text-sm font-medium text-equa-ink">
            Program
          </label>
          <select
            id="program_track"
            className="mt-1 w-full rounded-xl border border-equa-line/40 bg-[#0A0A14] px-3 py-2.5 text-sm text-equa-ink"
            {...form.register('program_track')}
          >
            <option value="">Seç…</option>
            {TRACK_OPTIONS.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <div>
            <label htmlFor="city" className="text-sm font-medium text-equa-ink">
              Şehir
            </label>
            <Input id="city" className="mt-1" {...form.register('city')} />
          </div>
          <div>
            <label htmlFor="district" className="text-sm font-medium text-equa-ink">
              İlçe
            </label>
            <Input id="district" className="mt-1" {...form.register('district')} />
          </div>
        </div>
        <div>
          <p className="text-sm font-medium text-equa-ink">Hobiler</p>
          <div className="mt-2 flex flex-wrap gap-2" role="group" aria-label="Hobiler">
            {HOBBY_OPTIONS.map((opt) => {
              const selected = hobbies.includes(opt)
              return (
                <button
                  key={opt}
                  type="button"
                  onClick={() => toggleList(hobbies, setHobbies, opt)}
                  className={[
                    'rounded-full px-3 py-1.5 text-xs font-medium',
                    selected
                      ? 'bg-equa-primary text-equa-on-primary'
                      : 'bg-equa-accent-soft text-equa-primary',
                  ].join(' ')}
                  aria-pressed={selected}
                >
                  {opt}
                </button>
              )
            })}
          </div>
          <div className="mt-2 flex gap-2">
            <Input
              value={customHobby}
              onChange={(e) => setCustomHobby(e.target.value)}
              placeholder="Özel hobi ekle…"
              aria-label="Özel hobi"
            />
            <Button
              type="button"
              variant="ghost"
              onClick={() => {
                const label = customHobby.trim()
                if (!label) return
                if (!hobbies.includes(label)) setHobbies([...hobbies, label])
                setCustomHobby('')
              }}
            >
              Ekle
            </Button>
          </div>
        </div>
        <div>
          <p className="text-sm font-medium text-equa-ink">Şarj olduğu şeyler</p>
          <div
            className="mt-2 flex flex-wrap gap-2"
            role="group"
            aria-label="Şarj aktiviteleri"
          >
            {RECHARGE_OPTIONS.map((opt) => {
              const selected = recharge.includes(opt)
              return (
                <button
                  key={opt}
                  type="button"
                  onClick={() => toggleList(recharge, setRecharge, opt)}
                  className={[
                    'rounded-full px-3 py-1.5 text-xs font-medium',
                    selected
                      ? 'bg-equa-primary text-equa-on-primary'
                      : 'bg-equa-accent-soft text-equa-primary',
                  ].join(' ')}
                  aria-pressed={selected}
                >
                  {opt}
                </button>
              )
            })}
          </div>
        </div>
        <div>
          <label htmlFor="bio" className="text-sm font-medium text-equa-ink">
            Kısa bio
          </label>
          <textarea
            id="bio"
            rows={3}
            {...form.register('bio')}
            className="mt-1 w-full rounded-xl border border-equa-line/40 bg-[#0A0A14] px-3 py-2.5 text-sm text-equa-ink focus:border-equa-primary focus:outline-none focus:ring-2 focus:ring-equa-primary/30"
          />
        </div>
        <Button type="submit" disabled={saveMutation.isPending}>
          {saveMutation.isPending ? 'Kaydediliyor…' : 'Kaydet'}
        </Button>
        {saveMutation.isSuccess ? (
          <p className="text-sm text-equa-primary">Profil güncellendi.</p>
        ) : null}
        {saveMutation.isError ? (
          <p className="text-sm text-red-300" role="alert">
            Kayıt başarısız.
          </p>
        ) : null}
      </form>

      <div>
        <h2 className="font-display text-base font-semibold text-equa-ink">
          LinkedIn PDF
        </h2>
        <div
          onDragOver={(e) => {
            e.preventDefault()
            setDragOver(true)
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
          className={[
            'mt-3 rounded-2xl border border-dashed px-4 py-8 text-center transition-colors',
            dragOver
              ? 'border-equa-primary bg-equa-accent-soft'
              : 'border-equa-line/40 bg-equa-surface/40',
          ].join(' ')}
        >
          <p className="text-sm text-equa-muted">
            PDF’yi buraya bırak veya seç (max 10 MB)
          </p>
          <Button
            variant="ghost"
            className="mt-3"
            onClick={() => fileRef.current?.click()}
            disabled={uploadMutation.isPending}
          >
            {uploadMutation.isPending ? 'Yükleniyor…' : 'Dosya seç'}
          </Button>
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.txt,application/pdf,text/plain"
            aria-label="LinkedIn PDF dosyası"
            className="sr-only"
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) uploadMutation.mutate(file)
            }}
          />
        </div>

        {uploadMsg ? (
          <p className="mt-2 text-sm text-equa-ink" role="status">
            {uploadMsg}
          </p>
        ) : null}

        {fallbackHint ? (
          <button
            type="button"
            className="mt-3 text-sm font-medium text-equa-primary underline"
            onClick={() =>
              navigate('/chat', {
                state: {
                  prefill:
                    'LinkedIn PDF’m okunamadı. Yetkinliklerimi ve deneyimimi kısaca anlatayım:',
                },
              })
            }
          >
            Sohbette eksik alanları tamamla
          </button>
        ) : null}

        {chips.length > 0 ? (
          <ul className="mt-4 flex flex-wrap gap-2" aria-label="Yetkinlikler">
            {chips.map((skill) => (
              <li
                key={skill}
                className="rounded-full bg-equa-accent-soft px-2.5 py-1 text-xs font-medium text-equa-primary"
              >
                {skill}
              </li>
            ))}
          </ul>
        ) : null}
      </div>
    </div>
  )
}
