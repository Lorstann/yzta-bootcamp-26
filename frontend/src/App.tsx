import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from '@/layouts/AppShell'
import { ChatPage } from '@/pages/ChatPage'
import { CheckinPage } from '@/pages/CheckinPage'
import { InstitutionPage } from '@/pages/InstitutionPage'
import { LoginPage } from '@/pages/LoginPage'
import { NotFoundPage } from '@/pages/NotFoundPage'
import { ProfilePage } from '@/pages/ProfilePage'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<AppShell />}>
        <Route index element={<Navigate to="/chat" replace />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="checkin" element={<CheckinPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="institution" element={<InstitutionPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
