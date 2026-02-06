/**
 * Authentication Utility Functions
 *
 * Helper functions for mocked authentication operations.
 * Handles user storage, token generation, and session persistence via localStorage.
 *
 * PHASE II: Pure mock authentication using localStorage (NO backend dependency).
 * PHASE III: These functions will be replaced by Better Auth SDK.
 *
 * Feature: 002-frontend-auth
 * Date: 2026-01-07
 */

import type { User, MockedUser } from '@/types/auth'

// localStorage keys
const MOCKED_USERS_KEY = 'mocked-users'
const AUTH_STATE_KEY = 'auth-state'

// Token expiry duration (24 hours)
const TOKEN_EXPIRY_MS = 24 * 60 * 60 * 1000

/**
 * Generate a UUID v4
 */
export function generateUserId(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

/**
 * Generate a mock token for Phase II authentication
 * Format: "mock-token-{userId}-{timestamp}"
 *
 * NOTE: This is PURE MOCK for Phase II only.
 * Phase III will use Better Auth SDK to generate real JWT tokens.
 */
export function generateToken(userId: string): string {
  const timestamp = Date.now()
  return `mock-token-${userId}-${timestamp}`
}

/**
 * Hash password (mocked - just returns plain text)
 * In real app, this would use bcrypt
 */
export function hashPassword(password: string): string {
  // MOCKED: In production, use bcrypt.hash()
  return password
}

/**
 * Verify password (mocked - simple string comparison)
 * In real app, this would use bcrypt.compare()
 */
export function verifyPassword(
  password: string,
  passwordHash: string
): boolean {
  // MOCKED: In production, use bcrypt.compare()
  return password === passwordHash
}

/**
 * Get all mocked users from localStorage
 */
export function getMockedUsers(): Record<string, MockedUser> {
  if (typeof window === 'undefined') return {}

  try {
    const stored = localStorage.getItem(MOCKED_USERS_KEY)
    if (!stored) return {}
    return JSON.parse(stored)
  } catch (error) {
    console.error('Error reading mocked users:', error)
    return {}
  }
}

/**
 * Save a mocked user to localStorage
 */
export function saveMockedUser(user: MockedUser): void {
  if (typeof window === 'undefined') return

  try {
    const users = getMockedUsers()
    users[user.email] = user
    localStorage.setItem(MOCKED_USERS_KEY, JSON.stringify(users))
  } catch (error) {
    console.error('Error saving mocked user:', error)
  }
}

/**
 * Get mocked user by email
 */
export function getMockedUserByEmail(
  email: string
): MockedUser | null {
  const users = getMockedUsers()
  return users[email] || null
}

/**
 * Check if email already exists
 */
export function emailExists(email: string): boolean {
  const users = getMockedUsers()
  return email in users
}

/**
 * Get auth state from localStorage
 */
export function getAuthState(): { user: User; token: string } | null {
  if (typeof window === 'undefined') return null

  try {
    const stored = localStorage.getItem(AUTH_STATE_KEY)
    if (!stored) return null
    return JSON.parse(stored)
  } catch (error) {
    console.error('Error reading auth state:', error)
    return null
  }
}

/**
 * Save auth state to localStorage
 */
export function saveAuthState(state: { user: User; token: string }): void {
  if (typeof window === 'undefined') return

  try {
    localStorage.setItem(AUTH_STATE_KEY, JSON.stringify(state))
  } catch (error) {
    console.error('Error saving auth state:', error)
  }
}

/**
 * Clear auth state from localStorage
 */
export function clearAuthState(): void {
  if (typeof window === 'undefined') return

  try {
    localStorage.removeItem(AUTH_STATE_KEY)
  } catch (error) {
    console.error('Error clearing auth state:', error)
  }
}

/**
 * Check if JWT token is expired
 * Decodes the JWT and checks the exp claim
 */
export function isTokenExpired(token: string): boolean {
  try {
    // Decode JWT payload (middle part of token)
    const parts = token.split('.')
    if (parts.length !== 3) return true

    // Decode base64 payload
    const payload = JSON.parse(atob(parts[1]))

    // Check expiration (exp is in seconds, Date.now() is in milliseconds)
    const now = Math.floor(Date.now() / 1000)
    return payload.exp < now
  } catch (error) {
    console.error('Error checking token expiry:', error)
    return true
  }
}

/**
 * Initialize mocked users database with test user
 * Called on app startup
 */
export function initializeMockedUsers(): void {
  if (typeof window === 'undefined') return

  const users = getMockedUsers()

  // Pre-populate test user if not exists
  if (!('test@example.com' in users)) {
    const testUser: MockedUser = {
      id: generateUserId(),
      email: 'test@example.com',
      name: 'test',
      passwordHash: hashPassword('password123'),
      createdAt: new Date().toISOString(),
    }
    saveMockedUser(testUser)
  }
}
