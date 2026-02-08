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
import type { Task, TaskFormData, PaginatedTaskResponse, TaskFilters, Reminder } from '@/types/task'

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
   * Get Tasks (Phase V: paginated with filters)
   *
   * Fetch tasks for authenticated user with optional filters.
   * Calls GET /api/{userId}/tasks with query parameters.
   */
  async getTasks(userId: string, filters?: TaskFilters): Promise<APIResponse<PaginatedTaskResponse>> {
    try {
      const params = new URLSearchParams()
      if (filters?.q) params.set('q', filters.q)
      if (filters?.completed !== undefined) params.set('completed', String(filters.completed))
      if (filters?.priority) params.set('priority', filters.priority)
      if (filters?.tag) params.set('tag', filters.tag)
      if (filters?.overdue) params.set('overdue', 'true')
      if (filters?.dueBefore) params.set('due_before', filters.dueBefore)
      if (filters?.dueAfter) params.set('due_after', filters.dueAfter)
      if (filters?.sortBy) params.set('sort_by', filters.sortBy)
      if (filters?.sortOrder) params.set('sort_order', filters.sortOrder)
      if (filters?.limit) params.set('limit', String(filters.limit))
      if (filters?.offset) params.set('offset', String(filters.offset))

      const qs = params.toString()
      const url = `${this.baseURL}/api/${userId}/tasks${qs ? `?${qs}` : ''}`

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      })

      if (!response.ok) {
        const data = await response.json().catch(() => ({}))
        return {
          success: false,
          data: null,
          error: data.detail || data.error || 'Failed to fetch tasks',
          statusCode: response.status,
        }
      }

      const data = await response.json()

      // Map snake_case backend response to camelCase frontend types
      const mapped: PaginatedTaskResponse = {
        tasks: data.tasks.map((t: any) => ({
          id: t.id,
          title: t.title,
          description: t.description || '',
          completed: t.completed,
          priority: t.priority || 'none',
          tags: t.tags || [],
          dueDate: t.due_date || null,
          isOverdue: t.is_overdue || false,
          recurrenceRule: t.recurrence_rule || null,
          recurrenceGroupId: t.recurrence_group_id || null,
          createdAt: new Date(t.created_at),
          updatedAt: t.updated_at ? new Date(t.updated_at) : undefined,
        })),
        total: data.total,
        limit: data.limit,
        offset: data.offset,
      }

      return { success: true, data: mapped, error: null, statusCode: 200 }
    } catch (error) {
      return { success: false, data: null, error: 'Network error - could not connect to server', statusCode: 500 }
    }
  }

  /**
   * Create Task (Phase V: with priority, tags, due date, recurrence)
   *
   * Calls POST /api/{userId}/tasks with Authorization header.
   */
  async createTask(userId: string, data: TaskFormData): Promise<APIResponse<Task>> {
    try {
      const body: any = {
        title: data.title,
        description: data.description || null,
      }
      if (data.priority) body.priority = data.priority
      if (data.tags && data.tags.length > 0) body.tags = data.tags
      if (data.dueDate) body.due_date = data.dueDate
      if (data.recurrenceRule) body.recurrence_rule = data.recurrenceRule

      const response = await fetch(`${this.baseURL}/api/${userId}/tasks`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      })

      const responseData = await response.json()

      if (!response.ok) {
        return { success: false, data: null, error: responseData.detail || 'Failed to create task', statusCode: response.status }
      }

      const task: Task = {
        id: responseData.id,
        title: responseData.title,
        description: responseData.description || '',
        completed: responseData.completed,
        priority: responseData.priority || 'none',
        tags: responseData.tags || [],
        dueDate: responseData.due_date || null,
        isOverdue: responseData.is_overdue || false,
        recurrenceRule: responseData.recurrence_rule || null,
        recurrenceGroupId: responseData.recurrence_group_id || null,
        createdAt: new Date(responseData.created_at),
        updatedAt: responseData.updated_at ? new Date(responseData.updated_at) : undefined,
      }

      return { success: true, data: task, error: null, statusCode: 201 }
    } catch (error) {
      return { success: false, data: null, error: 'Network error - could not connect to server', statusCode: 500 }
    }
  }

  /**
   * Update Task (Phase V: PATCH with all fields)
   *
   * Calls PATCH /api/{userId}/tasks/{id} with Authorization header.
   */
  async updateTask(
    userId: string,
    id: string,
    data: Partial<TaskFormData> & { completed?: boolean }
  ): Promise<APIResponse<Task>> {
    try {
      const body: any = {}
      if (data.title !== undefined) body.title = data.title
      if (data.description !== undefined) body.description = data.description
      if (data.completed !== undefined) body.completed = data.completed
      if (data.priority !== undefined) body.priority = data.priority
      if (data.tags !== undefined) body.tags = data.tags
      if (data.dueDate !== undefined) body.due_date = data.dueDate
      if (data.recurrenceRule !== undefined) body.recurrence_rule = data.recurrenceRule

      const response = await fetch(`${this.baseURL}/api/${userId}/tasks/${id}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      })

      const responseData = await response.json()

      if (!response.ok) {
        return { success: false, data: null, error: responseData.detail || 'Failed to update task', statusCode: response.status }
      }

      const task: Task = {
        id: responseData.id,
        title: responseData.title,
        description: responseData.description || '',
        completed: responseData.completed,
        priority: responseData.priority || 'none',
        tags: responseData.tags || [],
        dueDate: responseData.due_date || null,
        isOverdue: responseData.is_overdue || false,
        recurrenceRule: responseData.recurrence_rule || null,
        recurrenceGroupId: responseData.recurrence_group_id || null,
        createdAt: new Date(responseData.created_at),
        updatedAt: responseData.updated_at ? new Date(responseData.updated_at) : undefined,
      }

      return { success: true, data: task, error: null, statusCode: 200 }
    } catch (error) {
      return { success: false, data: null, error: 'Network error - could not connect to server', statusCode: 500 }
    }
  }

  /**
   * Delete Task
   *
   * Calls DELETE /api/{userId}/tasks/{id} with Authorization header.
   */
  async deleteTask(userId: string, id: string): Promise<APIResponse<void>> {
    try {
      const response = await fetch(`${this.baseURL}/api/${userId}/tasks/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      })

      if (!response.ok && response.status !== 204) {
        const data = await response.json().catch(() => ({}))
        return { success: false, data: null, error: data.detail || 'Failed to delete task', statusCode: response.status }
      }

      return { success: true, data: null, error: null, statusCode: 204 }
    } catch (error) {
      return { success: false, data: null, error: 'Network error - could not connect to server', statusCode: 500 }
    }
  }

  // ===========================================================================
  // Phase V: Tags & Reminders
  // ===========================================================================

  /**
   * Get Tags - distinct tags for autocomplete
   */
  async getTags(userId: string): Promise<APIResponse<string[]>> {
    try {
      const response = await fetch(`${this.baseURL}/api/${userId}/tags`, {
        headers: { 'Authorization': `Bearer ${this.token}` },
      })

      if (!response.ok) {
        return { success: false, data: null, error: 'Failed to fetch tags', statusCode: response.status }
      }

      const data = await response.json()
      return { success: true, data: data.tags || [], error: null, statusCode: 200 }
    } catch (error) {
      return { success: false, data: null, error: 'Network error', statusCode: 500 }
    }
  }

  /**
   * Get Reminders for a task
   */
  async getReminders(userId: string, taskId: string): Promise<APIResponse<Reminder[]>> {
    try {
      const response = await fetch(`${this.baseURL}/api/${userId}/tasks/${taskId}/reminders`, {
        headers: { 'Authorization': `Bearer ${this.token}` },
      })

      if (!response.ok) {
        return { success: false, data: null, error: 'Failed to fetch reminders', statusCode: response.status }
      }

      const data = await response.json()
      const reminders: Reminder[] = (data.reminders || []).map((r: any) => ({
        id: r.id,
        taskId: r.task_id,
        userId: r.user_id,
        triggerAt: r.trigger_at,
        status: r.status,
        createdAt: r.created_at,
      }))
      return { success: true, data: reminders, error: null, statusCode: 200 }
    } catch (error) {
      return { success: false, data: null, error: 'Network error', statusCode: 500 }
    }
  }

  /**
   * Create Reminder (absolute or relative)
   */
  async createReminder(
    userId: string,
    taskId: string,
    reminder: { triggerAt?: string; relativeToDue?: string }
  ): Promise<APIResponse<Reminder>> {
    try {
      const body: any = {}
      if (reminder.triggerAt) body.trigger_at = reminder.triggerAt
      if (reminder.relativeToDue) body.relative_to_due = reminder.relativeToDue

      const response = await fetch(`${this.baseURL}/api/${userId}/tasks/${taskId}/reminders`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      })

      const data = await response.json()

      if (!response.ok) {
        return { success: false, data: null, error: data.detail || 'Failed to create reminder', statusCode: response.status }
      }

      const mapped: Reminder = {
        id: data.id,
        taskId: data.task_id,
        userId: data.user_id,
        triggerAt: data.trigger_at,
        status: data.status,
        createdAt: data.created_at,
      }
      return { success: true, data: mapped, error: null, statusCode: 201 }
    } catch (error) {
      return { success: false, data: null, error: 'Network error', statusCode: 500 }
    }
  }

  /**
   * Delete Reminder
   */
  async deleteReminder(userId: string, taskId: string, reminderId: string): Promise<APIResponse<void>> {
    try {
      const response = await fetch(
        `${this.baseURL}/api/${userId}/tasks/${taskId}/reminders/${reminderId}`,
        {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${this.token}` },
        },
      )

      if (!response.ok && response.status !== 204) {
        return { success: false, data: null, error: 'Failed to delete reminder', statusCode: response.status }
      }

      return { success: true, data: null, error: null, statusCode: 204 }
    } catch (error) {
      return { success: false, data: null, error: 'Network error', statusCode: 500 }
    }
  }
}

// Export singleton instance
export const apiClient = new APIClient()
