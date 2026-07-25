import { NavLink } from 'react-router-dom'

export function BottomNav() {
  return (
    <nav
      className="fixed inset-x-0 bottom-0 z-20 border-t border-equa-line/60 bg-equa-surface/95 px-2 pb-[env(safe-area-inset-bottom)] backdrop-blur-sm lg:hidden"
      aria-label="Mobil navigasyon"
    >
      <ul className="mx-auto flex max-w-lg items-stretch justify-around">
        <li className="flex-1">
          <NavLink
            to="/chat"
            className={({ isActive }) =>
              [
                'flex flex-col items-center gap-0.5 px-2 py-2.5 text-xs font-medium no-underline transition-colors',
                isActive ? 'text-equa-accent' : 'text-equa-muted',
              ].join(' ')
            }
          >
            <ChatIcon />
            Sohbet
          </NavLink>
        </li>
        <li className="flex-1">
          <span
            className="flex cursor-not-allowed flex-col items-center gap-0.5 px-2 py-2.5 text-xs font-medium text-equa-line"
            aria-disabled="true"
            title="Yakında"
          >
            <CheckIcon />
            Check-in
          </span>
        </li>
        <li className="flex-1">
          <span
            className="flex cursor-not-allowed flex-col items-center gap-0.5 px-2 py-2.5 text-xs font-medium text-equa-line"
            aria-disabled="true"
            title="Yakında"
          >
            <ProfileIcon />
            Profil
          </span>
        </li>
      </ul>
    </nav>
  )
}

function ChatIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M4 6.5A2.5 2.5 0 0 1 6.5 4h11A2.5 2.5 0 0 1 20 6.5v7a2.5 2.5 0 0 1-2.5 2.5H10l-4 3.5V16H6.5A2.5 2.5 0 0 1 4 13.5v-7Z"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function CheckIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="8" stroke="currentColor" strokeWidth="1.75" />
      <path
        d="M8.5 12.5 11 15l4.5-5"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function ProfileIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="9" r="3.25" stroke="currentColor" strokeWidth="1.75" />
      <path
        d="M6 19c.8-3 3-4.5 6-4.5s5.2 1.5 6 4.5"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
      />
    </svg>
  )
}
