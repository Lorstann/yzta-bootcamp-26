import { Link } from 'react-router-dom'

export function BrandLogo({ to = '/dashboard' }: { to?: string }) {
  return (
    <Link
      to={to}
      className="font-display inline-flex flex-col no-underline"
      aria-label="Equa ana sayfa"
    >
      <span className="bg-gradient-to-r from-equa-primary to-equa-tertiary bg-clip-text text-2xl font-extrabold tracking-tight text-transparent lg:text-3xl">
        Equa
      </span>
      <span className="mt-0.5 text-[10px] font-bold uppercase tracking-widest text-equa-muted">
        AI Kariyer Koçu
      </span>
    </Link>
  )
}
