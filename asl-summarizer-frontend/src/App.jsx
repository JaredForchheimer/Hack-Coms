import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { DataProvider } from './context/DataContext'
import ProtectedRoute from './components/auth/ProtectedRoute/ProtectedRoute'
import LoginPage from './pages/LoginPage/LoginPage'
import HomePage from './pages/HomePage/HomePage'
import SourcesPage from './pages/SourcesPage/SourcesPage'
import SummariesPage from './pages/SummariesPage/SummariesPage'
import TranslationPage from './pages/TranslationPage/TranslationPage'
import CommunityPage from './pages/CommunityPage/CommunityPage'
import ErrorBoundary from './components/common/ErrorBoundary/ErrorBoundary'

function App() {
  console.log('App component rendering...')
  
  return (
    <ErrorBoundary>
      <AuthProvider>
        <DataProvider>
          <Router>
            <div className="App">
              <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/" element={
                  <ProtectedRoute>
                    <HomePage />
                  </ProtectedRoute>
                } />
                <Route path="/sources" element={
                  <ProtectedRoute>
                    <SourcesPage />
                  </ProtectedRoute>
                } />
                <Route path="/summaries" element={
                  <ProtectedRoute>
                    <SummariesPage />
                  </ProtectedRoute>
                } />
                <Route path="/translation" element={
                  <ProtectedRoute>
                    <TranslationPage />
                  </ProtectedRoute>
                } />
                <Route path="/community" element={
                  <ProtectedRoute>
                    <CommunityPage />
                  </ProtectedRoute>
                } />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </div>
          </Router>
        </DataProvider>
      </AuthProvider>
    </ErrorBoundary>
  )
}

export default App