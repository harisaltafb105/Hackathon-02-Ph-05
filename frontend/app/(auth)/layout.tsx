/**
 * Public Layout (Auth Route Group)
 *
 * Layout for authentication pages (/login, /register).
 * Redirects authenticated users to /dashboard.
 *
 * Feature: 002-frontend-auth
 * Task: T025 (US3)
 */

'use client'

import { useEffect, type ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/auth-context'

export default function AuthLayout({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    // If authenticated, redirect to dashboard
    if (!isLoading && isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, isLoading, router])

  // Show nothing while checking auth or redirecting
  if (isLoading || isAuthenticated) {
    return null
  }

  // Render auth pages for unauthenticated users
  return <>{children}</>
}
