import { Link } from 'react-router-dom'

export function BrandLogo() {
  return (
    <Link
      to="/chat"
      className="font-display inline-flex items-baseline gap-1.5 text-equa-ink no-underline"
      aria-label="Equa ana sayfa"
    >
      <span className="text-xl font-semibold tracking-tight lg:text-2xl">Equa</span>
      <span className="text-[0.65rem] font-medium uppercase tracking-widest text-equa-accent">
        coach
      </span>
    </Link>
  )
}
