import { Routes, Route, Navigate } from 'react-router-dom'
import { Suspense, lazy } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import Layout from './components/Layout'
import LoadingSpinner from './components/ui/LoadingSpinner'
import Login from './components/Login'

// Lazy load components for better performance
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Documents = lazy(() => import('./pages/Documents'))
const Entities = lazy(() => import('./pages/Entities'))
const Processing = lazy(() => import('./pages/Processing'))
const Projects = lazy(() => import('./pages/Projects'))
const ProjectDetail = lazy(() => import('./pages/ProjectDetail'))
const Settings = lazy(() => import('./pages/Settings'))

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading, hasCheckedAuth } = useAuth()
  
  if (isLoading || !hasCheckedAuth) {
    return <LoadingSpinner />
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

// Main App Routes
function AppRoutes() {
  const { isAuthenticated } = useAuth()
  
  return (
    <Routes>
      <Route path="/login" element={isAuthenticated ? <Navigate to="/" replace /> : <Login />} />
      
      <Route path="/" element={
        <ProtectedRoute>
          <Layout>
            <Suspense fallback={<LoadingSpinner />}>
              <Dashboard />
            </Suspense>
          </Layout>
        </ProtectedRoute>
      } />
      
      <Route path="/documents" element={
        <ProtectedRoute>
          <Layout>
            <Suspense fallback={<LoadingSpinner />}>
              <Documents />
            </Suspense>
          </Layout>
        </ProtectedRoute>
      } />
      
      <Route path="/entities" element={
        <ProtectedRoute>
          <Layout>
            <Suspense fallback={<LoadingSpinner />}>
              <Entities />
            </Suspense>
          </Layout>
        </ProtectedRoute>
      } />
      
      <Route path="/processing" element={
        <ProtectedRoute>
          <Layout>
            <Suspense fallback={<LoadingSpinner />}>
              <Processing />
            </Suspense>
          </Layout>
        </ProtectedRoute>
      } />
      
      <Route path="/projects" element={
        <ProtectedRoute>
          <Layout>
            <Suspense fallback={<LoadingSpinner />}>
              <Projects />
            </Suspense>
          </Layout>
        </ProtectedRoute>
      } />
      
      <Route path="/projects/:slug" element={
        <ProtectedRoute>
          <Layout>
            <Suspense fallback={<LoadingSpinner />}>
              <ProjectDetail />
            </Suspense>
          </Layout>
        </ProtectedRoute>
      } />
      
      <Route path="/settings" element={
        <ProtectedRoute>
          <Layout>
            <Suspense fallback={<LoadingSpinner />}>
              <Settings />
            </Suspense>
          </Layout>
        </ProtectedRoute>
      } />
      
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

function App() {
  return <AppRoutes />
}

export default App
