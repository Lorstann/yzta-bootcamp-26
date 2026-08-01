import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiPatch } from '@/shared/api/client'
import { getStoredUser, setAuth, getAccessToken } from '@/shared/auth/storage'

type Step = {
  id: string
  question: string
  kind: 'text' | 'capacity'
  skippable: boolean
}

const STEPS: Step[] = [
  {
    id: 'goals',
    question: 'Bootcamp’ten sonra neyi başarmak istiyorsun? (kısaca)',
    kind: 'text',
    skippable: true,
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

export function OnboardingPage() {
  const navigate = useNavigate()
  const [stepIndex, setStepIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [input, setInput] = useState('')
  const [capacity, setCapacity] = useState(70)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const step = STEPS[stepIndex]
  const progress = useMemo(
    () => Math.round(((stepIndex + 1) / STEPS.length) * 100),
    [stepIndex],
  )

  async function finish(finalCapacity: number, bioParts: string[]) {
    setSaving(true)
    setError(null)
    try {
      await apiPatch('/api/v1/profiles/me/onboarding', {
        capacity_score: finalCapacity,
        bio: bioParts.filter(Boolean).join(' · ') || null,
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

    if (stepIndex >= STEPS.length - 1) {
      const bioParts = STEPS.filter((s) => s.kind === 'text')
        .map((s) => nextAnswers[s.id])
        .filter(Boolean)
      const cap =
        step.kind === 'capacity' && !skipped
          ? Number(value) || capacity
          : Number(nextAnswers.capacity) || capacity
      await finish(cap, bioParts)
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
        ) : (
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
        )}

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
