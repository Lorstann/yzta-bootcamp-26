import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from '@/layouts/AppShell'
import { CalendarPage } from '@/pages/CalendarPage'
import { ChatPage } from '@/pages/ChatPage'
import { CheckinPage } from '@/pages/CheckinPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { InstitutionPage } from '@/pages/InstitutionPage'
import { LandingPage } from '@/pages/LandingPage'
import { LoginPage } from '@/pages/LoginPage'
import { NotFoundPage } from '@/pages/NotFoundPage'
import { OnboardingPage } from '@/pages/OnboardingPage'
import { ProfilePage } from '@/pages/ProfilePage'
import { TasksPage } from '@/pages/TasksPage'
import {
  RedirectIfAuthenticated,
  RequireAuth,
} from '@/shared/auth/RequireAuth'
import { RequireRole } from '@/shared/auth/RequireRole'
import { getAccessToken } from '@/shared/auth/storage'

function LandingOrRedirect() {
  if (getAccessToken()) {
    return <Navigate to="/dashboard" replace />
  }
  return <LandingPage />
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingOrRedirect />} />
      <Route
        path="/login"
        element={
          <RedirectIfAuthenticated>
            <LoginPage />
          </RedirectIfAuthenticated>
        }
      />
      <Route
        path="/onboarding"
        element={
          <RequireAuth>
            <OnboardingPage />
          </RequireAuth>
        }
      />
      <Route
        element={
          <RequireAuth>
            <AppShell />
          </RequireAuth>
        }
      >
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="checkin" element={<CheckinPage />} />
        <Route path="tasks" element={<TasksPage />} />
        <Route path="takvim" element={<CalendarPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route
          path="institution"
          element={
            <RequireRole roles={['instructor', 'admin']} fallback="/dashboard">
              <InstitutionPage />
            </RequireRole>
          }
        />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
