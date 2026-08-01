import { Bell, Settings } from 'lucide-react'
import { Avatar, Button } from '@/components/ui'
import { getStoredUser } from '@/shared/auth/storage'

function todayDateLabel(d = new Date()): string {
  return d.toLocaleDateString('tr-TR', {
    day: 'numeric',
    month: 'long',
  })
}

function avatarInitial(fullName: string | null | undefined, email: string | null | undefined): string {
  const name = fullName?.trim()
  if (name) return name.slice(0, 1).toUpperCase()
  if (email) return email.slice(0, 1).toUpperCase()
  return '?'
}

export function TopBar({
  title,
  subtitle,
}: {
  title?: string
  subtitle?: string
}) {
  const user = getStoredUser()
  const initial = avatarInitial(user?.full_name, user?.email)
  const alt = user?.full_name?.trim() || user?.email || 'Kullanıcı'

  return (
    <header className="flex h-16 shrink-0 items-center justify-between gap-3 border-b border-equa-line/20 bg-equa-bg/60 px-4 backdrop-blur-md lg:px-8">
      <div className="flex min-w-0 items-center gap-4">
        {title ? (
          <div className="min-w-0">
            <h1 className="truncate font-display text-lg font-bold text-equa-ink lg:text-xl">
              {title}
            </h1>
            {subtitle ? (
              <p className="truncate text-sm text-equa-muted">{subtitle}</p>
            ) : null}
          </div>
        ) : (
          <span className="border-b-2 border-equa-primary pb-0.5 text-[12px] font-bold uppercase tracking-wider text-equa-primary">
            {todayDateLabel()}
          </span>
        )}
      </div>
      <div className="flex items-center gap-2">
        <Button variant="icon" aria-label="Bildirimler">
          <Bell size={20} />
        </Button>
        <Button variant="icon" aria-label="Ayarlar">
          <Settings size={20} />
        </Button>
        <Avatar alt={alt} fallback={initial} size="sm" />
      </div>
    </header>
  )
}
