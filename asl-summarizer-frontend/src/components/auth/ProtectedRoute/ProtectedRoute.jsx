import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../../context/AuthContext'
import LoadingSpinner from '../../common/LoadingSpinner/LoadingSpinner'

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth()
  const location = useLocation()

  // TEMPORARY: Skip authentication for development
  // Remove this when authentication is properly set up
  const isDevelopment = import.meta.env.DEV || import.meta.env.NODE_ENV === 'development'
  
  if (isDevelopment) {
    console.log('Development mode: Skipping authentication')
    return children
  }

  if (isLoading) {
    return (
      <div className="protected-route-loading">
        <LoadingSpinner size="large" />
        <p>Checking authentication...</p>
      </div>
    )
  }

  if (!isAuthenticated) {
    // Redirect to login page with return url
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return children
}

export default ProtectedRoute