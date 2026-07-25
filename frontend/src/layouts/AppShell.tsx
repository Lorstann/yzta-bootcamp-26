import { NavLink, Outlet } from 'react-router-dom'
import { BrandLogo } from '@/components/BrandLogo'
import { BottomNav } from '@/components/BottomNav'

export function AppShell() {
  return (
    <div className="flex h-full min-h-0 flex-col overflow-x-hidden lg:flex-row">
      <aside className="hidden min-h-0 w-56 shrink-0 flex-col border-r border-equa-line/60 bg-equa-surface/70 px-4 py-6 backdrop-blur-sm lg:flex">
        <BrandLogo />
        <nav className="mt-10 flex flex-col gap-1" aria-label="Ana menü">
          <NavLink
            to="/chat"
            className={({ isActive }) =>
              [
                'rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-equa-accent text-white'
                  : 'text-equa-muted hover:bg-equa-accent-soft hover:text-equa-ink',
              ].join(' ')
            }
          >
            Sohbet
          </NavLink>
          <span
            className="cursor-not-allowed rounded-lg px-3 py-2.5 text-sm font-medium text-equa-line"
            aria-disabled="true"
            title="Yakında"
          >
            Check-in
          </span>
          <span
            className="cursor-not-allowed rounded-lg px-3 py-2.5 text-sm font-medium text-equa-line"
            aria-disabled="true"
            title="Yakında"
          >
            Profil
          </span>
        </nav>
      </aside>

      <div className="flex min-h-0 min-w-0 flex-1 flex-col">
        <header className="flex shrink-0 items-center gap-3 border-b border-equa-line/50 bg-equa-surface/80 px-4 py-3 backdrop-blur-sm lg:px-6">
          <div className="lg:hidden">
            <BrandLogo />
          </div>
          <p className="hidden text-sm text-equa-muted lg:block">
            Haftalık check-in ve kariyer koçluğu
          </p>
        </header>

        <main className="min-h-0 min-w-0 flex-1 overflow-y-auto overflow-x-hidden pb-[4.5rem] lg:pb-0">
          <Outlet />
        </main>

        <BottomNav />
      </div>
    </div>
  )
}
