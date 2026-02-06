/**
 * Authentication Context
 *
 * Provides authentication state and actions throughout the application.
 * Mirrors the pattern from task-context.tsx for consistency.
 *
 * Uses FastAPI backend with JWT authentication.
 * Backend issues JWT tokens which are stored in localStorage for session persistence.
 *
 * Feature: 002-frontend-auth
 * Date: 2026-01-08
 */

'use client'

import { createContext, useContext, useReducer, useEffect, type ReactNode } from 'react'
import type { AuthState, AuthAction } from '@/types/auth'
import {
  getAuthState,
  saveAuthState,
  clearAuthState,
  isTokenExpired,
  initializeMockedUsers,
} from '@/lib/auth-utils'
import { apiClient } from '@/lib/api-client'

// Initial state
const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  token: null,
  error: null,
}

// Reducer function
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'LOGIN_START':
    case 'REGISTER_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      }

    case 'LOGIN_SUCCESS':
    case 'REGISTER_SUCCESS':
    case 'RESTORE_SESSION':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      }

    case 'LOGIN_FAILURE':
    case 'REGISTER_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload.error,
      }

    case 'LOGOUT':
      return {
        ...initialState,
      }

    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      }

    default:
      return state
  }
}

// Context creation
const AuthStateContext = createContext<AuthState | undefined>(undefined)
const AuthActionsContext = createContext<React.Dispatch<AuthAction> | undefined>(undefined)

// Provider component
export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState)

  // No initialization needed - backend handles all user management

  // Restore session from localStorage on mount
  useEffect(() => {
    const savedAuth = getAuthState()
    if (savedAuth) {
      // Check if token is expired
      if (!isTokenExpired(savedAuth.token)) {
        // Restore session
        dispatch({
          type: 'RESTORE_SESSION',
          payload: {
            user: savedAuth.user,
            token: savedAuth.token,
          },
        })

        // Set token in API client
        apiClient.setToken(savedAuth.token)
      } else {
        // Token expired, clear auth
        clearAuthState()
      }
    }
  }, [])

  // Persist auth state to localStorage when it changes
  useEffect(() => {
    if (state.isAuthenticated && state.user && state.token) {
      saveAuthState({
        user: state.user,
        token: state.token,
      })

      // Update API client token
      apiClient.setToken(state.token)
    } else {
      clearAuthState()
      apiClient.setToken(null)
    }
  }, [state.isAuthenticated, state.user, state.token])

  return (
    <AuthStateContext.Provider value={state}>
      <AuthActionsContext.Provider value={dispatch}>
        {children}
      </AuthActionsContext.Provider>
    </AuthStateContext.Provider>
  )
}

// Hooks
export function useAuth(): AuthState {
  const context = useContext(AuthStateContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export function useAuthActions(): React.Dispatch<AuthAction> {
  const context = useContext(AuthActionsContext)
  if (context === undefined) {
    throw new Error('useAuthActions must be used within AuthProvider')
  }
  return context
}
