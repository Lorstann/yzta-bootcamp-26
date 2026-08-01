import type {
  ButtonHTMLAttributes,
  InputHTMLAttributes,
  ReactNode,
} from 'react'
import { forwardRef } from 'react'
import { X } from 'lucide-react'

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'icon'

const buttonStyles: Record<Variant, string> = {
  primary:
    'bg-gradient-to-r from-equa-primary-container to-equa-primary text-equa-on-primary shadow-[0_0_20px_rgba(207,188,255,0.2)] hover:shadow-[0_0_32px_rgba(207,188,255,0.35)] disabled:opacity-50',
  secondary:
    'border border-equa-line/40 bg-equa-surface/50 text-equa-ink hover:bg-equa-surface-high/80 disabled:opacity-50',
  ghost:
    'border border-equa-line/30 bg-transparent text-equa-muted hover:bg-equa-surface-high/50 hover:text-equa-ink disabled:opacity-50',
  danger:
    'border border-equa-error/40 bg-equa-error/10 text-equa-error hover:bg-equa-error/20 disabled:opacity-50',
  icon:
    'p-2 text-equa-muted hover:text-equa-primary hover:bg-equa-surface-high/50 disabled:opacity-50',
}

export function Button({
  variant = 'primary',
  className = '',
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant
  children: ReactNode
}) {
  return (
    <button
      type="button"
      className={[
        'inline-flex min-h-11 items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-bold transition-all duration-300 focus-ring',
        buttonStyles[variant],
        className,
      ].join(' ')}
      {...props}
    >
      {children}
    </button>
  )
}

export function GlassPanel({
  children,
  className = '',
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <div className={['glass-panel rounded-2xl', className].join(' ')}>
      {children}
    </div>
  )
}

export function Card({
  children,
  className = '',
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <div
      className={[
        'rounded-2xl border border-equa-line/30 bg-equa-surface/50 px-4 py-3 backdrop-blur-md',
        className,
      ].join(' ')}
    >
      {children}
    </div>
  )
}

export function Badge({
  children,
  tone = 'neutral',
  className = '',
}: {
  children: ReactNode
  tone?: 'neutral' | 'green' | 'yellow' | 'red' | 'accent' | 'cyan'
  className?: string
}) {
  const tones = {
    neutral: 'bg-equa-surface-high text-equa-muted',
    green: 'bg-emerald-500/15 text-emerald-300',
    yellow: 'bg-amber-500/15 text-amber-300',
    red: 'bg-red-500/15 text-red-300',
    accent: 'bg-equa-accent-soft text-equa-primary',
    cyan: 'bg-cyan-900/30 text-cyan-400 border border-cyan-800/50',
  }
  return (
    <span
      className={[
        'inline-flex items-center gap-1 rounded-md px-2.5 py-1 text-xs font-semibold uppercase tracking-wide transition-colors duration-300',
        tones[tone],
        className,
      ].join(' ')}
    >
      {children}
    </span>
  )
}

export function AiChip({
  children = 'AI Canlı',
  className = '',
}: {
  children?: ReactNode
  className?: string
}) {
  return (
    <Badge tone="cyan" className={className}>
      <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-cyan-400" />
      {children}
    </Badge>
  )
}

export function StatCard({
  label,
  value,
  delta,
  icon,
  className = '',
}: {
  label: string
  value: ReactNode
  delta?: ReactNode
  icon?: ReactNode
  className?: string
}) {
  return (
    <Card
      className={[
        'relative overflow-hidden p-6 hover:border-equa-primary/50',
        className,
      ].join(' ')}
    >
      {icon ? (
        <div className="pointer-events-none absolute -right-2 -top-2 text-6xl text-equa-primary/10">
          {icon}
        </div>
      ) : null}
      <p className="text-[12px] font-bold uppercase tracking-widest text-equa-muted">
        {label}
      </p>
      <p className="mt-3 font-display text-3xl font-extrabold text-equa-ink">
        {value}
      </p>
      {delta ? (
        <p className="mt-2 text-sm text-equa-muted">{delta}</p>
      ) : null}
    </Card>
  )
}

export function ProgressRing({
  value,
  label,
  size = 160,
  className = '',
}: {
  value: number
  label?: string
  size?: number
  className?: string
}) {
  const clamped = Math.max(0, Math.min(100, value))
  const r = 45
  const circumference = 2 * Math.PI * r
  const offset = circumference - (clamped / 100) * circumference

  return (
    <div
      className={['relative flex items-center justify-center', className].join(
        ' ',
      )}
      role="img"
      aria-label={`Kapasite skoru %${Math.round(clamped)}`}
      style={{ width: size, height: size }}
    >
      <svg
        className="h-full w-full -rotate-90 transform"
        viewBox="0 0 100 100"
        aria-hidden
      >
        <circle
          className="text-equa-surface-highest/50"
          cx="50"
          cy="50"
          r={r}
          fill="none"
          stroke="currentColor"
          strokeWidth="6"
        />
        <circle
          className="text-equa-primary drop-shadow-[0_0_8px_rgba(207,188,255,0.6)]"
          cx="50"
          cy="50"
          r={r}
          fill="none"
          stroke="currentColor"
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center">
        <span className="font-display text-3xl font-extrabold text-equa-ink">
          %{Math.round(clamped)}
        </span>
        {label ? (
          <span className="mt-1 text-[10px] font-bold uppercase tracking-wider text-equa-primary/80">
            {label}
          </span>
        ) : null}
      </div>
    </div>
  )
}

export function ProgressBar({
  value,
  className = '',
}: {
  value: number
  className?: string
}) {
  const clamped = Math.max(0, Math.min(100, value))
  return (
    <div
      className={[
        'h-1.5 w-full overflow-hidden rounded-full border border-equa-line/10 bg-equa-surface-high',
        className,
      ].join(' ')}
      role="progressbar"
      aria-valuenow={clamped}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      <div
        className="relative h-full rounded-full bg-gradient-to-r from-equa-primary to-equa-primary-container transition-all duration-500"
        style={{ width: `${clamped}%` }}
      >
        <div className="absolute inset-x-0 top-0 h-px bg-white/30" />
      </div>
    </div>
  )
}

export function Toggle({
  checked,
  onChange,
  label,
  id,
}: {
  checked: boolean
  onChange: (next: boolean) => void
  label: string
  id?: string
}) {
  const toggleId = id ?? `toggle-${label.replace(/\s+/g, '-').toLowerCase()}`
  return (
    <label
      htmlFor={toggleId}
      className="flex min-h-11 cursor-pointer items-center justify-between gap-4"
    >
      <span className="text-sm text-equa-ink">{label}</span>
      <button
        id={toggleId}
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={[
          'relative h-6 w-11 shrink-0 rounded-full transition-colors focus-ring',
          checked ? 'bg-equa-primary' : 'bg-equa-surface-highest',
        ].join(' ')}
      >
        <span
          className={[
            'absolute top-0.5 left-0.5 h-5 w-5 rounded-full bg-white transition-transform',
            checked ? 'translate-x-5' : 'translate-x-0',
          ].join(' ')}
        />
      </button>
    </label>
  )
}

export function Avatar({
  src,
  alt,
  fallback,
  size = 'md',
  className = '',
}: {
  src?: string | null
  alt: string
  fallback?: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}) {
  const sizes = { sm: 'h-8 w-8 text-xs', md: 'h-9 w-9 text-sm', lg: 'h-28 w-28 text-2xl' }
  return (
    <div
      className={[
        'flex shrink-0 items-center justify-center overflow-hidden rounded-full border-2 border-equa-line/40 bg-gradient-to-br from-equa-primary-container to-equa-primary font-bold text-equa-on-primary',
        sizes[size],
        className,
      ].join(' ')}
    >
      {src ? (
        <img src={src} alt={alt} className="h-full w-full object-cover" />
      ) : (
        <span aria-hidden>{fallback ?? alt.slice(0, 1).toUpperCase()}</span>
      )}
    </div>
  )
}

export function Modal({
  open,
  onClose,
  title,
  titleId,
  children,
}: {
  open: boolean
  onClose: () => void
  title: string
  titleId: string
  children: ReactNode
}) {
  if (!open) return null
  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-equa-bg/70 p-4 backdrop-blur-sm sm:items-center"
      role="presentation"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="glass-panel max-h-[85vh] w-full max-w-lg overflow-y-auto rounded-2xl p-6 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-start justify-between gap-3">
          <h2 id={titleId} className="font-display text-lg font-bold text-equa-ink">
            {title}
          </h2>
          <Button variant="icon" onClick={onClose} aria-label="Kapat">
            <X size={18} />
          </Button>
        </div>
        {children}
      </div>
    </div>
  )
}

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string
  description?: string
  action?: ReactNode
}) {
  return (
    <div className="flex min-h-[10rem] flex-col items-center justify-center text-center">
      <p className="font-display text-base font-medium text-equa-ink">{title}</p>
      {description ? (
        <p className="mt-2 max-w-xs text-sm text-equa-muted">{description}</p>
      ) : null}
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  )
}

export function Skeleton({ className = '' }: { className?: string }) {
  return (
    <div
      className={['animate-pulse rounded-xl bg-equa-line/30', className].join(
        ' ',
      )}
      aria-hidden
    />
  )
}

export const Input = forwardRef<
  HTMLInputElement,
  InputHTMLAttributes<HTMLInputElement>
>(function Input({ className = '', ...props }, ref) {
  return (
    <input
      ref={ref}
      className={[
        'w-full rounded-xl border border-equa-line/40 bg-[#0A0A14] px-3 py-2.5 text-equa-ink placeholder:text-equa-outline focus:border-equa-primary focus:outline-none focus:ring-2 focus:ring-equa-primary/30',
        className,
      ].join(' ')}
      {...props}
    />
  )
})
