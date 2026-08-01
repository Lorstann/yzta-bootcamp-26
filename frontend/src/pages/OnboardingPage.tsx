import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiPatch } from '@/shared/api/client'
import { getStoredUser, setAuth, getAccessToken } from '@/shared/auth/storage'

type StepKind = 'text' | 'capacity' | 'chips' | 'city' | 'track'

type Step = {
  id: string
  question: string
  kind: StepKind
  skippable: boolean
  options?: string[]
  multi?: boolean
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

const STEPS: Step[] = [
  {
    id: 'goals',
    question: 'Bootcamp’ten sonra neyi başarmak istiyorsun? (kısaca)',
    kind: 'text',
    skippable: true,
  },
  {
    id: 'track',
    question: 'Hangi programdasın?',
    kind: 'track',
    skippable: true,
    options: TRACK_OPTIONS,
  },
  {
    id: 'city',
    question: 'Hangi şehir ve ilçedesin? (etkinlik ve mekan önerileri için)',
    kind: 'city',
    skippable: true,
  },
  {
    id: 'hobbies',
    question: 'Neler yapmayı seversin? (birden fazla seçebilirsin)',
    kind: 'chips',
    skippable: true,
    options: HOBBY_OPTIONS,
    multi: true,
  },
  {
    id: 'recharge',
    question: 'Kafanı en çok ne dağıtıyor?',
    kind: 'chips',
    skippable: true,
    options: RECHARGE_OPTIONS,
    multi: true,
  },
  {
    id: 'pace',
    question: 'Bu dönem haftalık çalışma ritmin nasıl? (ör. akşamlar / hafta sonu)',
    kind: 'text',
    skippable: true,
  },
  {
    id: 'stress',
    question: 'Şu an stres seviyen nasıl? Bir cümle yeterli.',
    kind: 'text',
    skippable: true,
  },
  {
    id: 'capacity',
    question: 'Bu haftaki kapasiteni 0–100 arası puanla (100 = tamamen müsait).',
    kind: 'capacity',
    skippable: false,
  },
  {
    id: 'support',
    question: 'Equa’nın sana nasıl destek olmasını istersin?',
    kind: 'text',
    skippable: true,
  },
]

type CityAnswer = { city: string; district: string }

export function OnboardingPage() {
  const navigate = useNavigate()
  const [stepIndex, setStepIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [chipAnswers, setChipAnswers] = useState<Record<string, string[]>>({})
  const [cityAnswer, setCityAnswer] = useState<CityAnswer>({ city: '', district: '' })
  const [trackOther, setTrackOther] = useState('')
  const [customChip, setCustomChip] = useState('')
  const [input, setInput] = useState('')
  const [capacity, setCapacity] = useState(70)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const step = STEPS[stepIndex]
  const progress = useMemo(
    () => Math.round(((stepIndex + 1) / STEPS.length) * 100),
    [stepIndex],
  )

  const selectedChips = chipAnswers[step.id] ?? []

  function toggleChip(label: string) {
    setChipAnswers((prev) => {
      const current = prev[step.id] ?? []
      const next = current.includes(label)
        ? current.filter((x) => x !== label)
        : [...current, label]
      return { ...prev, [step.id]: next }
    })
  }

  async function finish(
    finalCapacity: number,
    bioParts: string[],
    nextAnswers: Record<string, string>,
    nextChips: Record<string, string[]>,
    nextCity: CityAnswer,
  ) {
    setSaving(true)
    setError(null)
    try {
      const trackRaw = nextAnswers.track || ''
      const program_track =
        trackRaw === 'Diğer' ? trackOther.trim() || null : trackRaw || null

      await apiPatch('/api/v1/profiles/me/onboarding', {
        capacity_score: finalCapacity,
        bio: bioParts.filter(Boolean).join(' · ') || null,
        city: nextCity.city.trim() || null,
        district: nextCity.district.trim() || null,
        program_track,
        interests: {
          hobbies: nextChips.hobbies ?? [],
          recharge: nextChips.recharge ?? [],
          notes: [],
        },
        onboarding_completed: true,
      })
      const token = getAccessToken()
      const user = getStoredUser()
      if (token && user) {
        setAuth(token, { ...user, onboarding_completed: true })
      }
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Kaydedilemedi')
    } finally {
      setSaving(false)
    }
  }

  async function advance(value: string, skipped = false) {
    const nextAnswers = {
      ...answers,
      [step.id]: skipped ? '' : value,
    }
    setAnswers(nextAnswers)
    setInput('')
    setCustomChip('')

    if (stepIndex >= STEPS.length - 1) {
      const bioParts = STEPS.filter((s) => s.kind === 'text')
        .map((s) => nextAnswers[s.id])
        .filter(Boolean)
      const cap =
        step.kind === 'capacity' && !skipped
          ? Number(value) || capacity
          : Number(nextAnswers.capacity) || capacity
      await finish(cap, bioParts, nextAnswers, chipAnswers, cityAnswer)
      return
    }
    setStepIndex((i) => i + 1)
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (step.kind === 'capacity') {
      void advance(String(capacity))
      return
    }
    if (step.kind === 'chips') {
      void advance((chipAnswers[step.id] ?? []).join(', ') || '')
      return
    }
    if (step.kind === 'city') {
      void advance(
        [cityAnswer.city, cityAnswer.district].filter(Boolean).join(' / '),
      )
      return
    }
    if (step.kind === 'track') {
      const selected = answers.track || input
      if (!selected && !step.skippable) {
        setError('Bir program seç veya yaz.')
        return
      }
      if (selected === 'Diğer' && !trackOther.trim() && !step.skippable) {
        setError('Programını yaz.')
        return
      }
      setError(null)
      void advance(selected || '')
      return
    }
    if (!input.trim() && !step.skippable) {
      setError('Bu soruyu yanıtlaman gerekiyor.')
      return
    }
    setError(null)
    void advance(input.trim())
  }

  return (
    <div className="mx-auto flex h-full max-w-lg flex-col px-4 py-8">
      <p className="text-xs font-medium uppercase tracking-wide text-equa-muted">
        Tanışma · {progress}%
      </p>
      <div
        className="mt-2 h-1.5 overflow-hidden rounded-full bg-equa-line/50"
        role="progressbar"
        aria-valuenow={progress}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className="h-full rounded-full bg-equa-primary transition-[width] duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>

      <h1 className="font-display mt-8 text-xl font-semibold text-equa-ink">
        Senin için dengeli bir plan
      </h1>
      <p className="mt-2 text-sm text-equa-muted">
        Yaklaşık 5 dakika. İstersen bazı soruları geçebilirsin.
      </p>

      <div
        className="mt-8 rounded-2xl border border-equa-line/40 bg-equa-surface/70 px-4 py-4 text-sm text-equa-ink animate-[fadeSlide_280ms_ease-out]"
        role="status"
      >
        {step.question}
      </div>

      <form onSubmit={onSubmit} className="mt-4 space-y-3">
        {step.kind === 'capacity' ? (
          <div>
            <label htmlFor="capacity-range" className="text-sm font-medium text-equa-ink">
              Kapasite: {capacity}
            </label>
            <input
              id="capacity-range"
              type="range"
              min={0}
              max={100}
              value={capacity}
              onChange={(e) => setCapacity(Number(e.target.value))}
              className="mt-2 w-full accent-equa-primary"
            />
          </div>
        ) : null}

        {step.kind === 'text' ? (
          <div>
            <label htmlFor="onboarding-answer" className="sr-only">
              Yanıtın
            </label>
            <textarea
              id="onboarding-answer"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              rows={3}
              className="w-full rounded-xl border border-equa-line/40 bg-[#0A0A14] px-3 py-2.5 text-sm text-equa-ink"
              placeholder="Kısa bir yanıt yaz…"
            />
          </div>
        ) : null}

        {step.kind === 'city' ? (
          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <label htmlFor="city" className="text-sm font-medium text-equa-ink">
                Şehir
              </label>
              <input
                id="city"
                value={cityAnswer.city}
                onChange={(e) =>
                  setCityAnswer((c) => ({ ...c, city: e.target.value }))
                }
                className="mt-1 w-full rounded-xl border border-equa-line/40 bg-[#0A0A14] px-3 py-2.5 text-sm text-equa-ink"
                placeholder="örn. İzmir"
              />
            </div>
            <div>
              <label htmlFor="district" className="text-sm font-medium text-equa-ink">
                İlçe
              </label>
              <input
                id="district"
                value={cityAnswer.district}
                onChange={(e) =>
                  setCityAnswer((c) => ({ ...c, district: e.target.value }))
                }
                className="mt-1 w-full rounded-xl border border-equa-line/40 bg-[#0A0A14] px-3 py-2.5 text-sm text-equa-ink"
                placeholder="örn. Bornova"
              />
            </div>
          </div>
        ) : null}

        {step.kind === 'track' ? (
          <div className="space-y-3">
            <div className="flex flex-wrap gap-2" role="group" aria-label="Program">
              {(step.options ?? []).map((opt) => {
                const selected = answers.track === opt
                return (
                  <button
                    key={opt}
                    type="button"
                    onClick={() => setAnswers((a) => ({ ...a, track: opt }))}
                    className={[
                      'rounded-full px-3 py-1.5 text-sm font-medium transition-colors',
                      selected
                        ? 'bg-equa-primary text-equa-on-primary'
                        : 'bg-equa-accent-soft text-equa-primary',
                    ].join(' ')}
                  >
                    {opt}
                  </button>
                )
              })}
            </div>
            {answers.track === 'Diğer' ? (
              <input
                value={trackOther}
                onChange={(e) => setTrackOther(e.target.value)}
                className="w-full rounded-xl border border-equa-line/40 bg-[#0A0A14] px-3 py-2.5 text-sm text-equa-ink"
                placeholder="Program adını yaz…"
                aria-label="Diğer program"
              />
            ) : null}
          </div>
        ) : null}

        {step.kind === 'chips' ? (
          <div className="space-y-3">
            <div className="flex flex-wrap gap-2" role="group" aria-label={step.question}>
              {(step.options ?? []).map((opt) => {
                const selected = selectedChips.includes(opt)
                return (
                  <button
                    key={opt}
                    type="button"
                    onClick={() => toggleChip(opt)}
                    className={[
                      'rounded-full px-3 py-1.5 text-sm font-medium transition-colors',
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
            <div className="flex gap-2">
              <input
                value={customChip}
                onChange={(e) => setCustomChip(e.target.value)}
                className="flex-1 rounded-xl border border-equa-line/40 bg-[#0A0A14] px-3 py-2.5 text-sm text-equa-ink"
                placeholder="Başka bir şey ekle…"
                aria-label="Özel seçenek"
              />
              <button
                type="button"
                className="rounded-xl border border-equa-line/40 px-3 py-2 text-sm text-equa-ink"
                onClick={() => {
                  const label = customChip.trim()
                  if (!label) return
                  toggleChip(label)
                  setCustomChip('')
                }}
              >
                Ekle
              </button>
            </div>
          </div>
        ) : null}

        {error ? (
          <p className="text-sm text-red-300" role="alert">
            {error}
          </p>
        ) : null}

        <div className="flex gap-2">
          {step.skippable ? (
            <button
              type="button"
              disabled={saving}
              onClick={() => void advance('', true)}
              className="rounded-xl border border-equa-line/40 px-4 py-2.5 text-sm font-medium text-equa-muted disabled:opacity-50"
            >
              Geç
            </button>
          ) : null}
          <button
            type="submit"
            disabled={saving}
            className="flex-1 rounded-xl bg-gradient-to-r from-equa-primary-container to-equa-primary px-4 py-2.5 text-sm font-bold text-equa-on-primary disabled:opacity-50"
          >
            {saving
              ? 'Kaydediliyor…'
              : stepIndex >= STEPS.length - 1
                ? 'Hazırsın'
                : 'Devam'}
          </button>
        </div>
      </form>
    </div>
  )
}
