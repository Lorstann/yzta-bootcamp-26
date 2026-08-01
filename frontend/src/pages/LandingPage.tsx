import { Link } from 'react-router-dom'
import { Bolt, Bot, ListChecks, LineChart, PlayCircle } from 'lucide-react'
import { Button, GlassPanel } from '@/components/ui'
import { getAccessToken } from '@/shared/auth/storage'

export function LandingPage() {
  const authed = Boolean(getAccessToken())

  return (
    <div className="relative min-h-full overflow-x-hidden">
      <div className="pointer-events-none fixed top-[-20%] left-[-10%] h-[50%] w-[50%] rounded-full bg-equa-primary/20 blur-[120px]" />
      <div className="pointer-events-none fixed right-[-10%] bottom-[-20%] h-[40%] w-[40%] rounded-full bg-equa-primary-container/20 blur-[100px]" />

      <header className="relative z-10 flex h-20 items-center justify-between px-6 lg:px-12">
        <span className="bg-gradient-to-r from-equa-primary to-equa-tertiary bg-clip-text font-display text-2xl font-extrabold lowercase text-transparent">
          equa
        </span>
        <div className="flex items-center gap-4">
          <Link
            to={authed ? '/dashboard' : '/login'}
            className="text-sm font-medium text-equa-ink no-underline hover:text-equa-primary"
          >
            Giriş Yap
          </Link>
          <Link to={authed ? '/dashboard' : '/login'} className="no-underline">
            <Button className="!rounded-full">Demoyu Gör</Button>
          </Link>
        </div>
      </header>

      <main className="relative z-10 mx-auto max-w-6xl px-6 pb-20 pt-8 lg:px-12 lg:pt-16">
        <section className="grid items-center gap-12 lg:grid-cols-2">
          <div>
            <span className="inline-flex items-center gap-2 rounded-full border border-equa-line/30 bg-equa-surface/60 px-3 py-1 text-[11px] font-bold uppercase tracking-widest text-equa-muted">
              <Bolt size={14} className="text-equa-tertiary" aria-hidden />
              Yeni Nesil Öğrenme Deneyimi
            </span>
            <h1 className="mt-6 font-display text-4xl font-extrabold leading-tight text-equa-ink lg:text-5xl">
              Haftalık{' '}
              <span className="text-equa-tertiary">koçun</span> hep yanında.
            </h1>
            <p className="mt-4 max-w-lg text-lg text-equa-muted">
              AI destekli kişisel koçun ile hedeflerini belirle, kapasiteni
              optimize et ve akışta kalarak potansiyelinin zirvesine ulaş.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to={authed ? '/dashboard' : '/login'} className="no-underline">
                <Button className="!rounded-full !px-8 uppercase tracking-wide">
                  Ücretsiz Başla
                </Button>
              </Link>
              <Button variant="ghost" className="!rounded-full">
                <PlayCircle size={18} aria-hidden />
                Nasıl Çalışır?
              </Button>
            </div>
          </div>

          <GlassPanel className="relative overflow-hidden p-0 shadow-2xl">
            <div className="flex items-center gap-3 border-b border-equa-line/20 px-4 py-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-equa-primary to-equa-primary-container">
                <Bot size={20} className="text-equa-on-primary" />
              </div>
              <div>
                <p className="font-bold text-equa-ink">Equa AI Koç</p>
                <p className="text-xs text-emerald-300">● Çevrimiçi</p>
              </div>
            </div>
            <div className="space-y-4 p-4 min-h-[220px]">
              <div
                className="ml-auto max-w-[85%] rounded-2xl rounded-tr-none bg-equa-primary/20 border border-equa-primary/30 px-4 py-3 text-sm animate-fade-up"
                style={{ animationDelay: '0.2s' }}
              >
                React Hooks haftası yoğun geçiyor, nasıl dengelerim?
              </div>
              <div
                className="max-w-[85%] rounded-2xl rounded-tl-none border border-equa-line/20 bg-equa-surface px-4 py-3 text-sm animate-fade-up"
                style={{ animationDelay: '0.8s' }}
              >
                16. Hafta müfredatına göre useEffect ve useCallback için Flow
                State seansları öneriyorum.
              </div>
            </div>
          </GlassPanel>
        </section>

        <section className="mt-20">
          <h2 className="text-center font-display text-2xl font-bold text-equa-ink lg:text-3xl">
            Sistematik Başarı, Veriyle Desteklenen Gelişim
          </h2>
          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {[
              {
                icon: <Bot className="text-equa-primary" />,
                title: 'AI Koç',
                body: 'Haftalık check-in ile hedeflerini birlikte netleştir.',
              },
              {
                icon: <ListChecks className="text-equa-tertiary" />,
                title: 'Haftalık Hedefler',
                body: 'En fazla 3 görev — kapasitenize göre dengelenir.',
              },
              {
                icon: <LineChart className="text-equa-cyan" />,
                title: 'Kapasite Takibi',
                body: 'Enerji ve ilerlemeyi görün, dropout riskini azaltın.',
              },
            ].map((f) => (
              <GlassPanel
                key={f.title}
                className="p-6 transition-transform hover:-translate-y-1"
              >
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-equa-surface-high">
                  {f.icon}
                </div>
                <h3 className="font-display text-lg font-bold text-equa-ink">
                  {f.title}
                </h3>
                <p className="mt-2 text-sm text-equa-muted">{f.body}</p>
              </GlassPanel>
            ))}
          </div>
        </section>
      </main>
    </div>
  )
}
