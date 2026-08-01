import { Navigate, useLocation } from 'react-router-dom'
import { getAccessToken, getStoredUser } from '@/shared/auth/storage'

/**
 * Redirects unauthenticated users to /login?next=<current path>.
 * Students with incomplete onboarding are sent to /onboarding
 * (except when already on that route).
 */
export function RequireAuth({ children }: { children: React.ReactNode }) {
  const location = useLocation()
  const token = getAccessToken()
  const user = getStoredUser()

  if (!token) {
    const next = `${location.pathname}${location.search}`
    return <Navigate to={`/login?next=${encodeURIComponent(next)}`} replace />
  }

  if (
    user?.role === 'student' &&
    user.onboarding_completed === false &&
    location.pathname !== '/onboarding'
  ) {
    return <Navigate to="/onboarding" replace />
  }

  if (
    user?.role === 'student' &&
    user.onboarding_completed === true &&
    location.pathname === '/onboarding'
  ) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

/**
 * Soft gate: already-authenticated users visiting /login go to their home.
 */
export function RedirectIfAuthenticated({
  children,
}: {
  children: React.ReactNode
}) {
  const token = getAccessToken()
  const user = getStoredUser()
  if (token && user) {
    if (user.role === 'student' && user.onboarding_completed === false) {
      return <Navigate to="/onboarding" replace />
    }
    const home = user.role === 'student' ? '/dashboard' : '/institution'
    return <Navigate to={home} replace />
  }
  return <>{children}</>
}
