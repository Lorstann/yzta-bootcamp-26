import { NavLink } from 'react-router-dom'
import {
  Home,
  MessageSquare,
  ClipboardCheck,
  ListTodo,
  Calendar,
  User,
  Building2,
  Bot,
  LogOut,
} from 'lucide-react'
import { clearAuth, getStoredUser } from '@/shared/auth/storage'

const linkClass = ({ isActive }: { isActive: boolean }) =>
  [
    'flex min-h-11 flex-col items-center justify-center gap-0.5 px-1 py-2 text-[10px] font-medium no-underline transition-colors',
    isActive ? 'text-equa-primary' : 'text-equa-muted',
  ].join(' ')

function isStaffRole(role: string | undefined): boolean {
  return role === 'instructor' || role === 'admin'
}

export function BottomNav() {
  const user = getStoredUser()
  const staff = isStaffRole(user?.role)

  function handleLogout() {
    clearAuth()
    window.location.href = '/login'
  }

  return (
    <nav
      className="fixed inset-x-0 bottom-0 z-20 border-t border-equa-line/30 bg-equa-surface/90 px-1 pb-[env(safe-area-inset-bottom)] backdrop-blur-md lg:hidden"
      aria-label="Mobil navigasyon"
    >
      {staff ? (
        <ul className="mx-auto flex max-w-lg items-stretch justify-around">
          <li className="flex-1">
            <NavLink to="/institution" end className={linkClass}>
              <Building2 size={20} aria-hidden />
              Kurum
            </NavLink>
          </li>
          <li className="flex-1">
            <NavLink to="/institution/assistant" className={linkClass}>
              <Bot size={20} aria-hidden />
              Asistan
            </NavLink>
          </li>
          <li className="flex-1">
            <NavLink to="/institution/profile" className={linkClass}>
              <User size={20} aria-hidden />
              Profil
            </NavLink>
          </li>
          <li className="flex-1">
            <button
              type="button"
              className="flex min-h-11 w-full flex-col items-center justify-center gap-0.5 px-1 py-2 text-[10px] font-medium text-equa-muted transition-colors hover:text-equa-primary"
              onClick={handleLogout}
            >
              <LogOut size={20} aria-hidden />
              Çıkış
            </button>
          </li>
        </ul>
      ) : (
        <ul className="mx-auto flex max-w-lg items-stretch justify-around">
          <li className="flex-1">
            <NavLink to="/dashboard" className={linkClass}>
              <Home size={20} aria-hidden />
              Ana Sayfa
            </NavLink>
          </li>
          <li className="flex-1">
            <NavLink to="/chat" className={linkClass}>
              <MessageSquare size={20} aria-hidden />
              Sohbet
            </NavLink>
          </li>
          <li className="flex-1">
            <NavLink to="/checkin" className={linkClass}>
              <ClipboardCheck size={20} aria-hidden />
              Check-in
            </NavLink>
          </li>
          <li className="flex-1">
            <NavLink to="/tasks" className={linkClass}>
              <ListTodo size={20} aria-hidden />
              Görevler
            </NavLink>
          </li>
          <li className="flex-1">
            <NavLink to="/takvim" className={linkClass}>
              <Calendar size={20} aria-hidden />
              Takvim
            </NavLink>
          </li>
          <li className="flex-1">
            <NavLink to="/profile" className={linkClass}>
              <User size={20} aria-hidden />
              Profil
            </NavLink>
          </li>
        </ul>
      )}
    </nav>
  )
}
