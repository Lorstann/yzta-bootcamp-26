import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <div className="mx-auto flex max-w-md flex-col items-center px-4 py-16 text-center">
      <p className="font-display text-4xl font-semibold text-equa-accent">404</p>
      <h1 className="font-display mt-3 text-xl font-semibold text-equa-ink">
        Sayfa bulunamadı
      </h1>
      <p className="mt-2 text-sm text-equa-muted">
        Aradığın sayfa yok veya taşınmış olabilir.
      </p>
      <Link
        to="/chat"
        className="mt-6 rounded-lg bg-equa-accent px-4 py-2.5 text-sm font-medium text-white no-underline transition-opacity hover:opacity-90"
      >
        Sohbete dön
      </Link>
    </div>
  )
}
