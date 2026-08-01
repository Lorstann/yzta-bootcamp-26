import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { login } from '@/shared/api/client'
import { getAccessToken } from '@/shared/auth/storage'
import { Button, GlassPanel, Input } from '@/components/ui'

const loginSchema = z.object({
  tenant_slug: z.string().min(2, 'Kurum slug gerekli'),
  email: z.string().email('Geçerli bir e-posta gir'),
  password: z.string().min(1, 'Şifre gerekli'),
})

type LoginForm = z.infer<typeof loginSchema>

function safeNext(
  raw: string | null,
  role: string,
  onboardingDone?: boolean,
): string {
  if (role === 'student' && onboardingDone === false) {
    return '/onboarding'
  }
  if (raw && raw.startsWith('/') && !raw.startsWith('//')) {
    if (role === 'student' && raw.startsWith('/institution')) {
      return '/dashboard'
    }
    return raw
  }
  return role === 'student' ? '/dashboard' : '/institution'
}

export function LoginPage() {
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      tenant_slug: 'bootcamp-alpha',
      email: 'test_student_alpha@equa.dev',
      password: 'password123',
    },
  })

  if (getAccessToken()) {
    return null
  }

  async function onSubmit(values: LoginForm) {
    try {
      const user = await login(values)
      navigate(
        safeNext(params.get('next'), user.role, user.onboarding_completed),
      )
    } catch (err) {
      setError('root', {
        message: err instanceof Error ? err.message : 'Giriş başarısız',
      })
    }
  }

  return (
    <div className="relative mx-auto flex min-h-full max-w-md flex-col justify-center px-4 py-10">
      <div className="pointer-events-none absolute top-[-10%] left-[-20%] h-64 w-64 rounded-full bg-equa-primary/20 blur-[100px]" />
      <GlassPanel className="relative z-10 p-8">
        <Link to="/" className="no-underline">
          <h1 className="bg-gradient-to-r from-equa-primary to-equa-tertiary bg-clip-text font-display text-3xl font-extrabold text-transparent">
            Equa
          </h1>
        </Link>
        <p className="mt-1 text-sm text-equa-muted">Hesabına giriş yap</p>

        <form
          onSubmit={handleSubmit(onSubmit)}
          className="mt-8 space-y-4"
          noValidate
        >
          <div>
            <label htmlFor="tenant" className="text-sm font-medium text-equa-ink">
              Kurum (slug)
            </label>
            <Input id="tenant" className="mt-1" {...register('tenant_slug')} />
            {errors.tenant_slug ? (
              <p className="mt-1 text-sm text-red-300" role="alert">
                {errors.tenant_slug.message}
              </p>
            ) : null}
          </div>
          <div>
            <label htmlFor="email" className="text-sm font-medium text-equa-ink">
              E-posta
            </label>
            <Input
              id="email"
              type="email"
              autoComplete="username"
              className="mt-1"
              {...register('email')}
            />
            {errors.email ? (
              <p className="mt-1 text-sm text-red-300" role="alert">
                {errors.email.message}
              </p>
            ) : null}
          </div>
          <div>
            <label htmlFor="password" className="text-sm font-medium text-equa-ink">
              Şifre
            </label>
            <Input
              id="password"
              type="password"
              autoComplete="current-password"
              className="mt-1"
              {...register('password')}
            />
            {errors.password ? (
              <p className="mt-1 text-sm text-red-300" role="alert">
                {errors.password.message}
              </p>
            ) : null}
          </div>
          {errors.root ? (
            <p className="text-sm text-red-300" role="alert">
              {errors.root.message}
            </p>
          ) : null}
          <Button type="submit" disabled={isSubmitting} className="w-full">
            {isSubmitting ? 'Giriş yapılıyor…' : 'Giriş yap'}
          </Button>
        </form>

        <p className="mt-4 text-center text-xs text-equa-muted">
          Demo: test_student_alpha@equa.dev / coordinator_alpha@equa.dev —
          password123
        </p>
      </GlassPanel>
    </div>
  )
}
