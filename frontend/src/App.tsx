import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from '@/layouts/AppShell'
import { CalendarPage } from '@/pages/CalendarPage'
import { ChatPage } from '@/pages/ChatPage'
import { CheckinPage } from '@/pages/CheckinPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { InstitutionAssistantPage } from '@/pages/InstitutionAssistantPage'
import { InstitutionCurriculumPage } from '@/pages/InstitutionCurriculumPage'
import { InstitutionPage } from '@/pages/InstitutionPage'
import { InstitutionProfilePage } from '@/pages/InstitutionProfilePage'
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
import { getAccessToken, getStoredUser } from '@/shared/auth/storage'

function homePathForRole(role: string | undefined): string {
  if (role === 'instructor' || role === 'admin') return '/institution'
  return '/dashboard'
}

function LandingOrRedirect() {
  if (getAccessToken()) {
    const user = getStoredUser()
    return <Navigate to={homePathForRole(user?.role)} replace />
  }
  return <LandingPage />
}

function StudentRoute({ children }: { children: React.ReactNode }) {
  return <RequireRole roles={['student']}>{children}</RequireRole>
}

function StaffRoute({ children }: { children: React.ReactNode }) {
  return (
    <RequireRole roles={['instructor', 'admin']}>{children}</RequireRole>
  )
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
        <Route
          path="dashboard"
          element={
            <StudentRoute>
              <DashboardPage />
            </StudentRoute>
          }
        />
        <Route
          path="chat"
          element={
            <StudentRoute>
              <ChatPage />
            </StudentRoute>
          }
        />
        <Route
          path="checkin"
          element={
            <StudentRoute>
              <CheckinPage />
            </StudentRoute>
          }
        />
        <Route
          path="tasks"
          element={
            <StudentRoute>
              <TasksPage />
            </StudentRoute>
          }
        />
        <Route
          path="takvim"
          element={
            <StudentRoute>
              <CalendarPage />
            </StudentRoute>
          }
        />
        <Route
          path="profile"
          element={
            <StudentRoute>
              <ProfilePage />
            </StudentRoute>
          }
        />
        <Route
          path="institution"
          element={
            <StaffRoute>
              <InstitutionPage />
            </StaffRoute>
          }
        />
        <Route
          path="institution/assistant"
          element={
            <StaffRoute>
              <InstitutionAssistantPage />
            </StaffRoute>
          }
        />
        <Route
          path="institution/curriculum"
          element={
            <StaffRoute>
              <InstitutionCurriculumPage />
            </StaffRoute>
          }
        />
        <Route
          path="institution/profile"
          element={
            <StaffRoute>
              <InstitutionProfilePage />
            </StaffRoute>
          }
        />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
