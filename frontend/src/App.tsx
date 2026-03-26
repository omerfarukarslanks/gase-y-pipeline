import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import DashboardLayout from './components/layout/DashboardLayout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import CreateVideo from './pages/CreateVideo'
import MyVideos from './pages/MyVideos'
import VideoDetail from './pages/VideoDetail'
import Templates from './pages/Templates'
import Analytics from './pages/Analytics'
import Calendar from './pages/Calendar'
import SocialAccounts from './pages/SocialAccounts'
import Settings from './pages/Settings'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="create" element={<CreateVideo />} />
        <Route path="videos" element={<MyVideos />} />
        <Route path="videos/:id" element={<VideoDetail />} />
        <Route path="templates" element={<Templates />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="calendar" element={<Calendar />} />
        <Route path="accounts" element={<SocialAccounts />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}
