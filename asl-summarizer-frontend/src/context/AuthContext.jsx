import React, { createContext, useContext, useReducer, useEffect } from 'react'
import { authService } from '../services/authService'

const AuthContext = createContext()

const initialState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  error: null
}

function authReducer(state, action) {
  switch (action.type) {
    case 'LOGIN_START':
      return {
        ...state,
        isLoading: true,
        error: null
      }
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
        error: null
      }
    case 'LOGIN_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload
      }
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
      }
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload
      }
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null
      }
    default:
      return state
  }
}

export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState)

  // Check for existing token on app load
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // TEMPORARY: Auto-login for development
        const isDevelopment = import.meta.env.DEV || import.meta.env.NODE_ENV === 'development'
        
        if (isDevelopment) {
          // Create a mock user for development
          const mockUser = {
            id: 'dev-user',
            email: 'developer@example.com',
            username: 'Developer'
          }
          const mockToken = 'dev-token-123'
          
          dispatch({
            type: 'LOGIN_SUCCESS',
            payload: { user: mockUser, token: mockToken }
          })
          return
        }

        const token = localStorage.getItem('authToken')
        if (token) {
          const user = await authService.verifyToken(token)
          dispatch({
            type: 'LOGIN_SUCCESS',
            payload: { user, token }
          })
        }
      } catch (error) {
        localStorage.removeItem('authToken')
        dispatch({ type: 'SET_LOADING', payload: false })
      } finally {
        dispatch({ type: 'SET_LOADING', payload: false })
      }
    }

    checkAuth()
  }, [])

  const login = async (email, password) => {
    dispatch({ type: 'LOGIN_START' })
    try {
      const response = await authService.login(email, password)
      localStorage.setItem('authToken', response.token)
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: response
      })
      return response
    } catch (error) {
      dispatch({
        type: 'LOGIN_FAILURE',
        payload: error.message || 'Login failed'
      })
      throw error
    }
  }

  const logout = async () => {
    try {
      await authService.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('authToken')
      dispatch({ type: 'LOGOUT' })
    }
  }

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' })
  }

  const value = {
    ...state,
    login,
    logout,
    clearError
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}