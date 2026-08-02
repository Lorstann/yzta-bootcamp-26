import { Link } from 'react-router-dom'
import logo from '@/assets/brand/logo.png'

export function BrandLogo({
  to = '/dashboard',
  showTagline = true,
  className = '',
}: {
  to?: string
  showTagline?: boolean
  className?: string
}) {
  return (
    <Link
      to={to}
      className={['font-display inline-flex flex-col no-underline', className]
        .filter(Boolean)
        .join(' ')}
      aria-label="Equa ana sayfa"
    >
      <img
        src={logo}
        alt="Equa"
        className="h-8 w-auto object-contain lg:h-10"
        decoding="async"
      />
      {showTagline ? (
        <span className="mt-0.5 text-[10px] font-bold uppercase tracking-widest text-equa-muted">
          AI Kariyer Koçu
        </span>
      ) : null}
    </Link>
  )
}
