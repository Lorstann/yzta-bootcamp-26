import { useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { apiGet, apiPatch, apiPostForm } from '@/shared/api/client'
import { getAccessToken } from '@/shared/auth/storage'

type Profile = {
  user_id: string
  capacity_score: number | null
  bio: string | null
  competencies: Record<string, unknown> | null
  onboarding_completed: boolean
}

export function ProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [capacity, setCapacity] = useState('70')
  const [bio, setBio] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [fallbackHint, setFallbackHint] = useState(false)

  useEffect(() => {
    if (!getAccessToken()) {
      setError('Profil için giriş gerekli.')
      return
    }
    void apiGet<Profile>('/api/v1/profiles/me')
      .then((p) => {
        setProfile(p)
        if (p.capacity_score != null) setCapacity(String(p.capacity_score))
        if (p.bio) setBio(p.bio)
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Hata'))
  }, [])

  async function saveOnboarding(e: FormEvent) {
    e.preventDefault()
    const updated = await apiPatch<Profile>('/api/v1/profiles/me/onboarding', {
      capacity_score: Number(capacity),
      bio,
      onboarding_completed: true,
    })
    setProfile(updated)
    setMessage('Profil güncellendi.')
  }

  async function onUpload(file: File) {
    const form = new FormData()
    form.append('file', file)
    const result = await apiPostForm<{
      competencies: Record<string, unknown>
      fallback_required: boolean
    }>('/api/v1/profiles/me/linkedin', form)
    setFallbackHint(result.fallback_required)
    setProfile((p) =>
      p ? { ...p, competencies: result.competencies } : p,
    )
    setMessage(
      result.fallback_required
        ? 'PDF okunamadı — sohbette eksik bilgileri tamamla.'
        : 'Yetkinlikler çıkarıldı.',
    )
  }

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

  if (!profile) {
    return <p className="p-6 text-sm text-equa-muted">Yükleniyor…</p>
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-6">
      <h1 className="font-display text-lg font-semibold">Profil</h1>
      <p className="mt-1 text-sm text-equa-muted">
        Onboarding: {profile.onboarding_completed ? 'tamam' : 'eksik'}
      </p>

      <form onSubmit={saveOnboarding} className="mt-6 space-y-4">
        <div>
          <label htmlFor="capacity" className="text-sm font-medium">
            Kapasite skoru (0–100)
          </label>
          <input
            id="capacity"
            type="number"
            min={0}
            max={100}
            value={capacity}
            onChange={(e) => setCapacity(e.target.value)}
            className="mt-1 w-full rounded-xl border border-equa-line bg-white/80 px-3 py-2.5 text-sm"
          />
        </div>
        <div>
          <label htmlFor="bio" className="text-sm font-medium">
            Kısa bio
          </label>
          <textarea
            id="bio"
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            rows={3}
            className="mt-1 w-full rounded-xl border border-equa-line bg-white/80 px-3 py-2.5 text-sm"
          />
        </div>
        <button
          type="submit"
          className="rounded-xl bg-equa-accent px-4 py-2.5 text-sm font-medium text-white"
        >
          Kaydet
        </button>
      </form>

      <div className="mt-8">
        <h2 className="font-display text-base font-semibold">LinkedIn PDF</h2>
        <input
          type="file"
          accept=".pdf,.txt"
          className="mt-2 block text-sm"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) void onUpload(file)
          }}
        />
        {fallbackHint ? (
          <p className="mt-2 text-sm text-amber-800">
            Chat fallback: sohbette yetkinliklerini anlat.
          </p>
        ) : null}
        {profile.competencies ? (
          <pre className="mt-3 overflow-auto rounded-xl bg-white/70 p-3 text-xs">
            {JSON.stringify(profile.competencies, null, 2)}
          </pre>
        ) : null}
      </div>

      {message ? <p className="mt-4 text-sm text-equa-accent">{message}</p> : null}
    </div>
  )
}
