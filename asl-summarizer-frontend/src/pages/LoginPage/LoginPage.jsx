import React, { useState, useEffect } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import Button from '../../components/common/Button/Button'
import './LoginPage.css'

const LoginPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [errors, setErrors] = useState({})
  const [showPassword, setShowPassword] = useState(false)
  
  const { login, isAuthenticated, isLoading, error, clearError } = useAuth()
  const location = useLocation()
  
  // Redirect if already authenticated
  const from = location.state?.from?.pathname || '/'
  
  useEffect(() => {
    // Clear any existing errors when component mounts
    clearError()
  }, [clearError])

  const validateForm = () => {
    const newErrors = {}
    
    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address'
    }
    
    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required'
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    
    // Clear field error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
    
    // Clear auth error when user modifies form
    if (error) {
      clearError()
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }
    
    try {
      await login(formData.email, formData.password)
    } catch (err) {
      // Error is handled by AuthContext
      console.error('Login failed:', err)
    }
  }

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword)
  }

  // Demo credentials helper
  const fillDemoCredentials = () => {
    setFormData({
      email: 'demo@example.com',
      password: 'password123'
    })
    setErrors({})
    clearError()
  }

  if (isAuthenticated) {
    return <Navigate to={from} replace />
  }

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h1 className="login-title">ASL Article Summarizer</h1>
          <p className="login-subtitle">Sign in to access your account</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          {error && (
            <div className="login-error">
              <span className="login-error__icon">⚠️</span>
              <span className="login-error__message">{error}</span>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email Address
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              className={`form-input ${errors.email ? 'form-input--error' : ''}`}
              placeholder="Enter your email"
              autoComplete="email"
            />
            {errors.email && (
              <span className="form-error">{errors.email}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Password
            </label>
            <div className="password-input-container">
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className={`form-input ${errors.password ? 'form-input--error' : ''}`}
                placeholder="Enter your password"
                autoComplete="current-password"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={togglePasswordVisibility}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
            {errors.password && (
              <span className="form-error">{errors.password}</span>
            )}
          </div>

          <Button
            type="submit"
            variant="primary"
            size="large"
            loading={isLoading}
            className="login-button"
          >
            Sign In
          </Button>

          <div className="login-demo">
            <p className="login-demo__text">
              Want to try the demo?
            </p>
            <Button
              type="button"
              variant="ghost"
              size="medium"
              onClick={fillDemoCredentials}
              className="login-demo__button"
            >
              Use Demo Credentials
            </Button>
          </div>
        </form>

        <div className="login-footer">
          <p className="login-footer__text">
            Demo credentials: demo@example.com / password123
          </p>
        </div>
      </div>
    </div>
  )
}

export default LoginPage