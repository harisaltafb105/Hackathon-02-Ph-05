/**
 * API Client Singleton
 *
 * Centralized API client for all backend operations.
 * Calls FastAPI backend with JWT authentication.
 *
 * Feature: 002-frontend-auth
 * Date: 2026-01-08
 */

import type { User, APIResponse } from '@/types/auth'
import type { Task, TaskFormData } from '@/types/task'

/**
 * Generate a UUID v4
 */
function generateUserId(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

/**
 * API Client Class
 *
 * Singleton class providing all API methods.
 * Communicates with FastAPI backend at http://localhost:8000
 */
class APIClient {
  private baseURL = 'http://localhost:8000' // FastAPI backend endpoint
  private token: string | null = null

  /**
   * Set authentication token
   */
  setToken(token: string | null): void {
    this.token = token
  }

  /**
   * Get current authentication token
   */
  getToken(): string | null {
    return this.token
  }

  /**
   * Simulate network delay (300-800ms)
   */
  private async delay(ms?: number): Promise<void> {
    const delayTime = ms !== undefined ? ms : 300 + Math.random() * 500
    return new Promise((resolve) => setTimeout(resolve, delayTime))
  }

  /**
   * Login
   *
   * Authenticate user with email and password.
   * Calls backend POST /auth/login endpoint.
   */
  async login(
    email: string,
    password: string
  ): Promise<APIResponse<{ user: User; token: string }>> {
    try {
      const response = await fetch(`${this.baseURL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      })

      const data = await response.json()

      if (!response.ok) {
        return {
          success: false,
          data: null,
          error: data.detail || data.error || 'Login failed',
          statusCode: response.status,
        }
      }

      // Backend returns { user: {...}, token: "..." }
      return {
        success: true,
        data: {
          user: {
            id: data.user.id,
            email: data.user.email,
            name: data.user.name,
            createdAt: data.user.created_at,
          },
          token: data.token,
        },
        error: null,
        statusCode: response.status,
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: 'Network error - could not connect to server',
        statusCode: 500,
      }
    }
  }

  /**
   * Register
   *
   * Create new user account.
   * Calls backend POST /auth/register endpoint.
   */
  async register(
    email: string,
    password: string
  ): Promise<APIResponse<{ user: User; token: string }>> {
    try {
      // Extract name from email
      const name = email.split('@')[0]

      const response = await fetch(`${this.baseURL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, name }),
      })

      const data = await response.json()

      if (!response.ok) {
        return {
          success: false,
          data: null,
          error: data.detail || data.error || 'Registration failed',
          statusCode: response.status,
        }
      }

      // Backend returns { user: {...}, token: "..." }
      return {
        success: true,
        data: {
          user: {
            id: data.user.id,
            email: data.user.email,
            name: data.user.name,
            createdAt: data.user.created_at,
          },
          token: data.token,
        },
        error: null,
        statusCode: response.status,
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: 'Network error - could not connect to server',
        statusCode: 500,
      }
    }
  }

  /**
   * Logout
   *
   * Clear authentication token.
   * Mocked: Just clears token, actual cleanup happens in auth context.
   */
  async logout(): Promise<APIResponse<void>> {
    await this.delay()

    try {
      this.token = null

      return {
        success: true,
        data: null,
        error: null,
        statusCode: 200,
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: 'An unexpected error occurred',
        statusCode: 500,
      }
    }
  }

  /**
   * Get Tasks
   *
   * Fetch all tasks for authenticated user.
   * Mocked: Returns empty array (task-context manages actual tasks).
   * Future: Will call GET /api/tasks with Authorization header.
   */
  async getTasks(): Promise<APIResponse<Task[]>> {
    await this.delay()

    try {
      // Mocked: Return empty array
      // In real implementation, this will fetch from backend
      return {
        success: true,
        data: [],
        error: null,
        statusCode: 200,
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: 'An unexpected error occurred',
        statusCode: 500,
      }
    }
  }

  /**
   * Create Task
   *
   * Create new task for authenticated user.
   * Mocked: Returns mocked task (task-context manages actual tasks).
   * Future: Will call POST /api/tasks with Authorization header.
   */
  async createTask(data: TaskFormData): Promise<APIResponse<Task>> {
    await this.delay()

    try {
      // Mocked: Return mocked task
      // In real implementation, this will post to backend
      const mockedTask: Task = {
        id: generateUserId(),
        title: data.title,
        description: data.description || '',
        completed: false,
        createdAt: new Date(),
      }

      return {
        success: true,
        data: mockedTask,
        error: null,
        statusCode: 200,
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: 'An unexpected error occurred',
        statusCode: 500,
      }
    }
  }

  /**
   * Update Task
   *
   * Update existing task for authenticated user.
   * Mocked: Returns mocked task (task-context manages actual tasks).
   * Future: Will call PATCH /api/tasks/{id} with Authorization header.
   */
  async updateTask(
    id: string,
    data: Partial<TaskFormData>
  ): Promise<APIResponse<Task>> {
    await this.delay()

    try {
      // Mocked: Return mocked task
      // In real implementation, this will patch to backend
      const mockedTask: Task = {
        id,
        title: data.title || 'Updated Task',
        description: data.description || '',
        completed: false,
        createdAt: new Date(),
        updatedAt: new Date(),
      }

      return {
        success: true,
        data: mockedTask,
        error: null,
        statusCode: 200,
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: 'An unexpected error occurred',
        statusCode: 500,
      }
    }
  }

  /**
   * Delete Task
   *
   * Delete task for authenticated user.
   * Mocked: Returns success (task-context manages actual tasks).
   * Future: Will call DELETE /api/tasks/{id} with Authorization header.
   */
  async deleteTask(id: string): Promise<APIResponse<void>> {
    await this.delay()

    try {
      // Mocked: Return success
      // In real implementation, this will delete from backend
      return {
        success: true,
        data: null,
        error: null,
        statusCode: 200,
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: 'An unexpected error occurred',
        statusCode: 500,
      }
    }
  }
}

// Export singleton instance
export const apiClient = new APIClient()
