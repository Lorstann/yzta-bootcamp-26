import { Navigate } from 'react-router-dom'
import { getStoredUser } from '@/shared/auth/storage'

type Role = 'student' | 'instructor' | 'admin'

/**
 * Role-based route gate. Must be nested under RequireAuth.
 */
export function RequireRole({
  roles,
  children,
  fallback = '/chat',
}: {
  roles: Role[]
  children: React.ReactNode
  fallback?: string
}) {
  const user = getStoredUser()
  if (!user || !roles.includes(user.role as Role)) {
    return <Navigate to={fallback} replace />
  }
  return <>{children}</>
}
