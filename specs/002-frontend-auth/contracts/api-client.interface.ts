/**
 * API Client Interface Contract
 *
 * This file defines the interface for the API client used throughout the application.
 * All methods return APIResponse<T> for consistent error handling and type safety.
 *
 * Current Implementation: Mocked (frontend-only)
 * Future Implementation: Real fetch calls to FastAPI backend
 *
 * Feature: 002-frontend-auth
 * Date: 2026-01-07
 */

import type { User, APIResponse } from '@/types/auth'
import type { Task, CreateTaskInput, UpdateTaskInput } from '@/types/task'

/**
 * Authentication Endpoints
 */
export interface AuthAPI {
  /**
   * Authenticate user with email and password
   *
   * @param email - User email address
   * @param password - User password (plain text, will be hashed by backend)
   * @returns APIResponse with user data and JWT token
   *
   * Success Response (200):
   * {
   *   success: true,
   *   data: { user: User, token: string },
   *   error: null,
   *   statusCode: 200
   * }
   *
   * Failure Response (401):
   * {
   *   success: false,
   *   data: null,
   *   error: "Invalid email or password",
   *   statusCode: 401
   * }
   */
  login(email: string, password: string): Promise<APIResponse<{ user: User; token: string }>>

  /**
   * Register new user account
   *
   * @param email - User email address (must be unique)
   * @param password - User password (plain text, will be hashed by backend)
   * @returns APIResponse with user data and JWT token
   *
   * Success Response (200):
   * {
   *   success: true,
   *   data: { user: User, token: string },
   *   error: null,
   *   statusCode: 200
   * }
   *
   * Failure Response (400):
   * {
   *   success: false,
   *   data: null,
   *   error: "Email already registered",
   *   statusCode: 400
   * }
   */
  register(email: string, password: string): Promise<APIResponse<{ user: User; token: string }>>

  /**
   * Logout current user (clear token)
   *
   * @returns APIResponse with void data
   *
   * Success Response (200):
   * {
   *   success: true,
   *   data: null,
   *   error: null,
   *   statusCode: 200
   * }
   */
  logout(): Promise<APIResponse<void>>
}

/**
 * Task CRUD Endpoints
 */
export interface TaskAPI {
  /**
   * Fetch all tasks for authenticated user
   *
   * @returns APIResponse with array of tasks
   *
   * Requires: Authorization header with valid JWT token
   *
   * Success Response (200):
   * {
   *   success: true,
   *   data: [{ id, title, description, completed, createdAt, updatedAt }],
   *   error: null,
   *   statusCode: 200
   * }
   *
   * Unauthorized Response (401):
   * {
   *   success: false,
   *   data: null,
   *   error: "Unauthorized - Invalid or missing token",
   *   statusCode: 401
   * }
   */
  getTasks(): Promise<APIResponse<Task[]>>

  /**
   * Create new task for authenticated user
   *
   * @param data - Task creation data (title, description)
   * @returns APIResponse with created task
   *
   * Requires: Authorization header with valid JWT token
   *
   * Success Response (200):
   * {
   *   success: true,
   *   data: { id, title, description, completed, createdAt, updatedAt },
   *   error: null,
   *   statusCode: 200
   * }
   */
  createTask(data: CreateTaskInput): Promise<APIResponse<Task>>

  /**
   * Update existing task for authenticated user
   *
   * @param id - Task ID to update
   * @param data - Task update data (title, description, completed)
   * @returns APIResponse with updated task
   *
   * Requires: Authorization header with valid JWT token
   *
   * Success Response (200):
   * {
   *   success: true,
   *   data: { id, title, description, completed, createdAt, updatedAt },
   *   error: null,
   *   statusCode: 200
   * }
   *
   * Not Found Response (404):
   * {
   *   success: false,
   *   data: null,
   *   error: "Task not found",
   *   statusCode: 404
   * }
   */
  updateTask(id: string, data: UpdateTaskInput): Promise<APIResponse<Task>>

  /**
   * Delete task for authenticated user
   *
   * @param id - Task ID to delete
   * @returns APIResponse with void data
   *
   * Requires: Authorization header with valid JWT token
   *
   * Success Response (200):
   * {
   *   success: true,
   *   data: null,
   *   error: null,
   *   statusCode: 200
   * }
   */
  deleteTask(id: string): Promise<APIResponse<void>>
}

/**
 * Complete API Client Interface
 *
 * Combines auth and task endpoints into single client interface
 */
export interface IAPIClient extends AuthAPI, TaskAPI {
  /**
   * Get current authentication token
   * Used internally for header injection
   */
  getToken(): string | null

  /**
   * Set authentication token
   * Called after successful login/register
   */
  setToken(token: string | null): void
}

/**
 * Expected Backend Endpoints (FastAPI)
 *
 * When backend is implemented, these are the expected routes:
 *
 * POST   /api/auth/login           - Login with email/password
 * POST   /api/auth/register        - Register new user
 * POST   /api/auth/logout          - Logout (optional, can be client-side only)
 *
 * GET    /api/tasks                - Get all tasks for user
 * POST   /api/tasks                - Create new task
 * PATCH  /api/tasks/{id}           - Update task
 * DELETE /api/tasks/{id}           - Delete task
 *
 * All protected endpoints require:
 * Authorization: Bearer <jwt-token>
 *
 * All responses follow APIResponse<T> structure
 */

/**
 * Implementation Notes
 *
 * Mocked Implementation (Current):
 * - All methods simulate network delay (300-800ms)
 * - Auth methods check localStorage "mocked-users"
 * - Task methods use existing task-context state
 * - Token format: "mock-token-{userId}"
 *
 * Real Implementation (Future):
 * - Replace mocked methods with fetch() calls
 * - Use real JWT tokens from Better Auth
 * - Connect to FastAPI backend endpoints
 * - Add retry logic and advanced error handling
 * - No interface changes needed - just implementation swap
 */
