import { Bell, Settings } from 'lucide-react'
import { Avatar, Button } from '@/components/ui'

function isoWeekLabel(d = new Date()): string {
  const tmp = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()))
  const dayNum = tmp.getUTCDay() || 7
  tmp.setUTCDate(tmp.getUTCDate() + 4 - dayNum)
  const yearStart = new Date(Date.UTC(tmp.getUTCFullYear(), 0, 1))
  const week = Math.ceil(((tmp.getTime() - yearStart.getTime()) / 86400000 + 1) / 7)
  return `${week}. Hafta`
}

export function TopBar({
  title,
  subtitle,
}: {
  title?: string
  subtitle?: string
}) {
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
            {isoWeekLabel()}
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
        <Avatar alt="Öğrenci" fallback="Ö" size="sm" />
      </div>
    </header>
  )
}
