import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import {
  Home,
  MessageSquare,
  ClipboardCheck,
  ListTodo,
  Calendar,
  User,
  Building2,
  Bot,
  Rocket,
  LogOut,
  BookOpen,
} from 'lucide-react'
import { BrandLogo } from '@/components/BrandLogo'
import { BottomNav } from '@/components/BottomNav'
import { InstallPrompt } from '@/components/InstallPrompt'
import { TopBar } from '@/components/TopBar'
import { Button } from '@/components/ui'
import { clearAuth, getStoredUser } from '@/shared/auth/storage'

const navClass = ({ isActive }: { isActive: boolean }) =>
  [
    'flex items-center gap-3 rounded-xl px-4 py-3 text-sm transition-all duration-300 hover:translate-x-1',
    isActive
      ? 'border-l-4 border-equa-primary bg-equa-primary/10 font-bold text-equa-primary'
      : 'border-l-4 border-transparent text-equa-muted hover:bg-equa-surface-highest/40',
  ].join(' ')

function isStaffRole(role: string | undefined): boolean {
  return role === 'instructor' || role === 'admin'
}

export function AppShell() {
  const user = getStoredUser()
  const navigate = useNavigate()
  const staff = isStaffRole(user?.role)

  function handleLogout() {
    clearAuth()
    window.location.href = '/login'
  }

  return (
    <div className="flex h-full min-h-0 flex-col overflow-x-hidden lg:flex-row">
      <aside className="hidden min-h-0 w-64 shrink-0 flex-col gap-4 border-r border-equa-line/20 bg-equa-bg/80 p-4 backdrop-blur-xl lg:flex">
        <div className="mt-2 px-2">
          <BrandLogo />
        </div>
        <nav className="mt-4 flex flex-col gap-1" aria-label="Ana menü">
          {staff ? (
            <>
              <NavLink to="/institution" end className={navClass}>
                <Building2 size={20} aria-hidden />
                Kurum
              </NavLink>
              <NavLink to="/institution/assistant" className={navClass}>
                <Bot size={20} aria-hidden />
                Asistan
              </NavLink>
              <NavLink to="/institution/curriculum" className={navClass}>
                <BookOpen size={20} aria-hidden />
                Müfredat
              </NavLink>
              <NavLink to="/institution/profile" className={navClass}>
                <User size={20} aria-hidden />
                Profil
              </NavLink>
            </>
          ) : (
            <>
              <NavLink to="/dashboard" className={navClass}>
                <Home size={20} aria-hidden />
                Ana Sayfa
              </NavLink>
              <NavLink to="/chat" className={navClass}>
                <MessageSquare size={20} aria-hidden />
                Sohbet
              </NavLink>
              <NavLink to="/checkin" className={navClass}>
                <ClipboardCheck size={20} aria-hidden />
                Check-in
              </NavLink>
              <NavLink to="/tasks" className={navClass}>
                <ListTodo size={20} aria-hidden />
                Görevler
              </NavLink>
              <NavLink to="/takvim" className={navClass}>
                <Calendar size={20} aria-hidden />
                Takvim
              </NavLink>
              <NavLink to="/profile" className={navClass}>
                <User size={20} aria-hidden />
                Profil
              </NavLink>
            </>
          )}
        </nav>
        <div className="mt-auto space-y-3">
          {staff ? (
            <Button
              className="w-full"
              onClick={() => navigate('/institution/assistant')}
            >
              <Bot size={18} aria-hidden />
              Asistan
            </Button>
          ) : (
            <Button className="w-full" onClick={() => navigate('/chat')}>
              <Rocket size={18} aria-hidden />
              Check-in Başlat
            </Button>
          )}
          {user ? (
            <button
              type="button"
              className="flex w-full items-center gap-2 text-left text-xs text-equa-muted underline hover:text-equa-primary"
              onClick={handleLogout}
            >
              <LogOut size={14} aria-hidden />
              Çıkış ({user.email})
            </button>
          ) : (
            <NavLink
              to="/login"
              className="text-xs text-equa-primary underline"
            >
              Giriş yap
            </NavLink>
          )}
        </div>
      </aside>

      <div className="flex min-h-0 min-w-0 flex-1 flex-col">
        <div className="flex items-center gap-3 border-b border-equa-line/20 bg-equa-bg/60 px-4 py-3 backdrop-blur-md lg:hidden">
          <BrandLogo />
        </div>
        <div className="hidden lg:block">
          <TopBar />
        </div>

        <main className="min-h-0 min-w-0 flex-1 overflow-y-auto overflow-x-hidden pb-[4.5rem] lg:pb-0">
          <Outlet />
        </main>

        <InstallPrompt />
        <BottomNav />
      </div>
    </div>
  )
}
