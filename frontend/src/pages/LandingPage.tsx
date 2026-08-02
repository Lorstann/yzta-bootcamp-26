import { Link } from 'react-router-dom'
import logo from '@/assets/brand/logo.png'
import { BrandLogo } from '@/components/BrandLogo'
import { Button } from '@/components/ui'
import { getAccessToken, getStoredUser } from '@/shared/auth/storage'

function authedHome(): string {
  if (!getAccessToken()) return '/login'
  const user = getStoredUser()
  return user?.role === 'student' ? '/dashboard' : '/institution'
}

const STEPS = [
  {
    n: '01',
    title: 'Check-in',
    body: 'Haftalık AI check-in ile durumunu iki dakikada paylaş.',
  },
  {
    n: '02',
    title: 'En fazla 3 görev',
    body: 'Kapasitenize göre dengelenmiş, yutulabilir aksiyonlar.',
  },
  {
    n: '03',
    title: 'Akışta kal',
    body: 'Enerji ve ilerlemeyi birlikte izle; tempoyu koru.',
  },
] as const

export function LandingPage() {
  const home = authedHome()

  return (
    <div className="relative min-h-full overflow-x-hidden bg-equa-bg">
      {/* —— Hero —— */}
      <section className="relative flex min-h-[100svh] flex-col">
        <div className="absolute inset-0 overflow-hidden" aria-hidden>
          <div
            className="absolute inset-0 scale-105 bg-cover bg-center motion-safe:animate-hero-ken"
            style={{ backgroundImage: 'url(/images/landing-hero.png)' }}
          />
          <div className="absolute inset-0 bg-gradient-to-b from-equa-bg/85 via-equa-bg/55 to-equa-bg" />
          <div className="absolute inset-0 bg-gradient-to-r from-equa-bg/70 via-transparent to-equa-bg/40" />
        </div>

        <header className="relative z-10 flex h-20 shrink-0 items-center justify-between px-6 lg:px-12">
          <BrandLogo to="/" showTagline={false} />
          <Link
            to={home}
            className="text-sm font-medium text-equa-ink no-underline transition-colors hover:text-equa-tertiary"
          >
            Giriş Yap
          </Link>
        </header>

        <div className="relative z-10 flex flex-1 flex-col justify-end px-6 pb-16 pt-8 lg:px-12 lg:pb-24">
          <div className="max-w-xl">
            <img
              src={logo}
              alt="Equa"
              className="animate-fade-up h-12 w-auto object-contain lg:h-16"
              decoding="async"
            />
            <h1 className="animate-fade-up animation-delay-100 mt-8 font-display text-4xl font-extrabold leading-[1.1] tracking-tight text-equa-ink lg:text-6xl">
              Kapasiteni aşmadan ilerle.
            </h1>
            <p className="animate-fade-up animation-delay-200 mt-5 max-w-md text-lg leading-relaxed text-equa-muted lg:text-xl">
              Haftalık AI check-in ve en fazla 3 görev — bootcamp temposunu
              sürdürülebilir tut.
            </p>
            <div className="animate-fade-up animation-delay-300 mt-9 flex flex-wrap items-center gap-3">
              <Link to={home} className="no-underline">
                <Button className="!rounded-full !px-8">Başla</Button>
              </Link>
              <a href="#nasil-calisir" className="no-underline">
                <Button variant="ghost" className="!rounded-full">
                  Nasıl çalışır?
                </Button>
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* —— How it works —— */}
      <section
        id="nasil-calisir"
        className="relative scroll-mt-8 px-6 py-20 lg:px-12 lg:py-28"
      >
        <div className="mx-auto max-w-4xl">
          <h2 className="font-display text-3xl font-bold tracking-tight text-equa-ink lg:text-4xl">
            Üç adımda denge
          </h2>
          <p className="mt-3 max-w-lg text-equa-muted">
            Yoğun programı parçala; sürdürülebilir bir ritim kur.
          </p>

          <ol className="mt-14 space-y-0 divide-y divide-equa-line/25">
            {STEPS.map((step) => (
              <li
                key={step.n}
                className="grid gap-2 py-8 first:pt-0 last:pb-0 sm:grid-cols-[4rem_1fr] sm:gap-8"
              >
                <span className="font-display text-sm font-bold tabular-nums tracking-widest text-equa-tertiary">
                  {step.n}
                </span>
                <div>
                  <h3 className="font-display text-xl font-semibold text-equa-ink">
                    {step.title}
                  </h3>
                  <p className="mt-2 max-w-md text-equa-muted">{step.body}</p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {/* —— Institution —— */}
      <section className="relative min-h-[70svh] overflow-hidden">
        <div className="absolute inset-0" aria-hidden>
          <div
            className="absolute inset-0 bg-cover bg-center"
            style={{
              backgroundImage: 'url(/images/institution-hero.png)',
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-b from-equa-bg via-equa-bg/75 to-equa-bg" />
          <div className="absolute inset-0 bg-equa-bg/40" />
        </div>

        <div className="relative z-10 mx-auto flex min-h-[70svh] max-w-4xl flex-col justify-center px-6 py-20 lg:px-12">
          <h2 className="font-display text-3xl font-bold tracking-tight text-equa-ink lg:text-4xl">
            Dropout’u tahmin etmeden yakala.
          </h2>
          <p className="mt-4 max-w-lg text-lg text-equa-muted">
            Risk sinyalleri ve korunan gelir — mentör müdahalesini günler değil
            saatler içinde başlat.
          </p>
          <div className="mt-8">
            <Link to={home} className="no-underline">
              <Button className="!rounded-full !px-8">
                Kurum paneline gir
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <footer className="border-t border-equa-line/20 px-6 py-8 lg:px-12">
        <div className="mx-auto flex max-w-4xl items-center justify-between gap-4">
          <BrandLogo to="/" showTagline={false} />
          <Link
            to={home}
            className="text-sm text-equa-muted no-underline transition-colors hover:text-equa-ink"
          >
            Giriş Yap
          </Link>
        </div>
      </footer>
    </div>
  )
}
