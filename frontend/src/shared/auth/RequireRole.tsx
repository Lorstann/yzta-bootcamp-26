import { Navigate } from 'react-router-dom'
import { getStoredUser } from '@/shared/auth/storage'

type Role = 'student' | 'instructor' | 'admin'

function defaultFallback(role: string | undefined): string {
  if (role === 'instructor' || role === 'admin') return '/institution'
  return '/dashboard'
}

/**
 * Role-based route gate. Must be nested under RequireAuth.
 * When `fallback` is omitted, students go to /dashboard and staff to /institution.
 */
export function RequireRole({
  roles,
  children,
  fallback,
}: {
  roles: Role[]
  children: React.ReactNode
  fallback?: string
}) {
  const user = getStoredUser()
  if (!user || !roles.includes(user.role as Role)) {
    return <Navigate to={fallback ?? defaultFallback(user?.role)} replace />
  }
  return <>{children}</>
}
