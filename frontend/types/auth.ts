/**
 * Authentication Type Definitions
 *
 * This file defines all types related to authentication and user management.
 * All types are designed to match expected backend structures for seamless future integration.
 *
 * Feature: 002-frontend-auth
 * Date: 2026-01-07
 */

/**
 * User Entity
 *
 * Represents an authenticated user in the system.
 */
export interface User {
  id: string // Unique user identifier (UUID format)
  email: string // User email (unique, validated format)
  name: string // Display name
  createdAt: string // ISO 8601 timestamp (e.g., "2026-01-07T10:30:00Z")
}

/**
 * Auth State
 *
 * Represents the current authentication state of the application.
 */
export interface AuthState {
  user: User | null // Currently authenticated user (null if not authenticated)
  isAuthenticated: boolean // Derived: true if user !== null
  isLoading: boolean // True during async auth operations (login, register, logout)
  token: string | null // Mocked JWT token (format: "mock-token-{userId}")
  error: string | null // Last authentication error message
}

/**
 * Auth Actions
 *
 * Discriminated union of all possible authentication actions.
 */
export type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'LOGIN_FAILURE'; payload: { error: string } }
  | { type: 'REGISTER_START' }
  | { type: 'REGISTER_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'REGISTER_FAILURE'; payload: { error: string } }
  | { type: 'LOGOUT' }
  | { type: 'CLEAR_ERROR' }
  | { type: 'RESTORE_SESSION'; payload: { user: User; token: string } }

/**
 * API Response
 *
 * Generic response structure for all API operations (mocked and future real API).
 */
export interface APIResponse<T = any> {
  success: boolean // True if operation succeeded
  data: T | null // Response payload (type varies by endpoint)
  error: string | null // Error message if failed (null if success)
  statusCode: number // HTTP status code (200, 401, 403, 500, etc.)
}

/**
 * Login Form Data
 *
 * Form data structure for login page validation.
 */
export interface LoginFormData {
  email: string
  password: string
}

/**
 * Register Form Data
 *
 * Form data structure for registration page validation.
 */
export interface RegisterFormData {
  email: string
  password: string
  confirmPassword: string
}

/**
 * Mocked User (Internal)
 *
 * Internal structure for mocked user database (not exposed to frontend components).
 * Note: In real app, password would be bcrypt hashed.
 */
export interface MockedUser {
  id: string // UUID
  email: string // Unique email
  name: string // Display name
  passwordHash: string // Plain text password (mocked only - real app uses bcrypt)
  createdAt: string // ISO 8601 timestamp
}
