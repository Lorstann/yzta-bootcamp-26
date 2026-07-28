import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { login } from '@/shared/api/client'

export function LoginPage() {
  const navigate = useNavigate()
  const [tenantSlug, setTenantSlug] = useState('bootcamp-alpha')
  const [email, setEmail] = useState('test_student_alpha@equa.dev')
  const [password, setPassword] = useState('password123')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const user = await login({
        tenant_slug: tenantSlug,
        email,
        password,
      })
      navigate(user.role === 'student' ? '/chat' : '/institution')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Giriş başarısız')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto flex min-h-full max-w-md flex-col justify-center px-4 py-10">
      <h1 className="font-display text-2xl font-semibold text-equa-ink">Equa</h1>
      <p className="mt-1 text-sm text-equa-muted">Hesabına giriş yap</p>

      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        <div>
          <label htmlFor="tenant" className="text-sm font-medium text-equa-ink">
            Kurum (slug)
          </label>
          <input
            id="tenant"
            value={tenantSlug}
            onChange={(e) => setTenantSlug(e.target.value)}
            className="mt-1 w-full rounded-xl border border-equa-line bg-white/80 px-3 py-2.5 text-sm"
          />
        </div>
        <div>
          <label htmlFor="email" className="text-sm font-medium text-equa-ink">
            E-posta
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded-xl border border-equa-line bg-white/80 px-3 py-2.5 text-sm"
          />
        </div>
        <div>
          <label htmlFor="password" className="text-sm font-medium text-equa-ink">
            Şifre
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded-xl border border-equa-line bg-white/80 px-3 py-2.5 text-sm"
          />
        </div>
        {error ? (
          <p className="text-sm text-red-700" role="alert">
            {error}
          </p>
        ) : null}
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-xl bg-equa-accent py-2.5 text-sm font-medium text-white disabled:opacity-50"
        >
          {loading ? 'Giriş yapılıyor…' : 'Giriş yap'}
        </button>
      </form>

      <p className="mt-4 text-center text-sm text-equa-muted">
        Demo: student / coordinator_alpha@equa.dev — password123
      </p>
      <p className="mt-2 text-center text-sm">
        <Link to="/chat" className="text-equa-accent underline">
          Misafir olarak sohbete git
        </Link>
      </p>
    </div>
  )
}
