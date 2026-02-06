'use client'

import React, { createContext, useContext, useReducer, useEffect, useCallback, type ReactNode } from 'react'
import type { Task, AppState, TaskAction, FilterType } from '@/types/task'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * Get auth token from localStorage
 */
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null
  const authData = localStorage.getItem('auth-state')
  if (!authData) return null
  try {
    const parsed = JSON.parse(authData)
    return parsed.token || null
  } catch {
    return null
  }
}

/**
 * Get user ID from localStorage
 */
function getUserId(): string | null {
  if (typeof window === 'undefined') return null
  const authData = localStorage.getItem('auth-state')
  if (!authData) return null
  try {
    const parsed = JSON.parse(authData)
    return parsed.user?.id || null
  } catch {
    return null
  }
}

// Initial state - start with empty tasks, will load from API
const initialState: AppState = {
  tasks: [],
  ui: {
    activeFilter: 'all',
    modalOpen: false,
    modalMode: null,
    editingTaskId: null,
    isLoading: false,
    error: null,
  },
}

// Task reducer with all actions
function taskReducer(state: AppState, action: TaskAction): AppState {
  switch (action.type) {
    case 'SET_TASKS': {
      return {
        ...state,
        tasks: action.payload,
      }
    }

    case 'ADD_TASK': {
      return {
        ...state,
        tasks: [...state.tasks, action.payload as Task],
      }
    }

    case 'UPDATE_TASK': {
      return {
        ...state,
        tasks: state.tasks.map((task) =>
          task.id === action.payload.id
            ? { ...task, ...action.payload.updates, updatedAt: new Date() }
            : task
        ),
      }
    }

    case 'DELETE_TASK': {
      return {
        ...state,
        tasks: state.tasks.filter((task) => task.id !== action.payload),
      }
    }

    case 'TOGGLE_COMPLETE': {
      return {
        ...state,
        tasks: state.tasks.map((task) =>
          task.id === action.payload ? { ...task, completed: !task.completed } : task
        ),
      }
    }

    case 'SET_FILTER': {
      return {
        ...state,
        ui: { ...state.ui, activeFilter: action.payload },
      }
    }

    case 'OPEN_MODAL': {
      return {
        ...state,
        ui: {
          ...state.ui,
          modalOpen: true,
          modalMode: action.payload.mode,
          editingTaskId: action.payload.taskId || null,
        },
      }
    }

    case 'CLOSE_MODAL': {
      return {
        ...state,
        ui: {
          ...state.ui,
          modalOpen: false,
          modalMode: null,
          editingTaskId: null,
        },
      }
    }

    case 'SET_LOADING': {
      return {
        ...state,
        ui: { ...state.ui, isLoading: action.payload },
      }
    }

    case 'SET_ERROR': {
      return {
        ...state,
        ui: { ...state.ui, error: action.payload },
      }
    }

    default:
      return state
  }
}

// Context type with API actions
interface TaskContextType {
  state: AppState
  dispatch: React.Dispatch<TaskAction>
  fetchTasks: () => Promise<void>
  addTask: (title: string, description?: string) => Promise<void>
  updateTask: (id: string, updates: { title?: string; description?: string; completed?: boolean }) => Promise<void>
  deleteTask: (id: string) => Promise<void>
  toggleComplete: (id: string) => Promise<void>
}

// Create context
const TaskContext = createContext<TaskContextType | undefined>(undefined)

// Provider component
export function TaskProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(taskReducer, initialState)

  // Fetch tasks from backend
  const fetchTasks = useCallback(async () => {
    const token = getAuthToken()
    const userId = getUserId()

    if (!token || !userId) {
      return
    }

    dispatch({ type: 'SET_LOADING', payload: true })

    try {
      const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        // Transform backend response to frontend format
        const tasks: Task[] = data.map((task: any) => ({
          id: task.id,
          title: task.title,
          description: task.description || '',
          completed: task.completed,
          createdAt: new Date(task.created_at),
          updatedAt: task.updated_at ? new Date(task.updated_at) : undefined,
        }))
        dispatch({ type: 'SET_TASKS', payload: tasks })
      }
    } catch (error) {
      console.error('Error fetching tasks:', error)
      dispatch({ type: 'SET_ERROR', payload: 'Failed to load tasks' })
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }, [])

  // Add task via API
  const addTask = useCallback(async (title: string, description?: string) => {
    const token = getAuthToken()
    const userId = getUserId()

    if (!token || !userId) {
      dispatch({ type: 'SET_ERROR', payload: 'Not authenticated' })
      return
    }

    dispatch({ type: 'SET_LOADING', payload: true })

    try {
      const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ title, description }),
      })

      if (response.ok) {
        const data = await response.json()
        const newTask: Task = {
          id: data.id,
          title: data.title,
          description: data.description || '',
          completed: data.completed,
          createdAt: new Date(data.created_at),
        }
        dispatch({ type: 'ADD_TASK', payload: newTask })
      } else {
        const error = await response.json()
        dispatch({ type: 'SET_ERROR', payload: error.detail || 'Failed to add task' })
      }
    } catch (error) {
      console.error('Error adding task:', error)
      dispatch({ type: 'SET_ERROR', payload: 'Failed to add task' })
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }, [])

  // Update task via API
  const updateTask = useCallback(async (id: string, updates: { title?: string; description?: string; completed?: boolean }) => {
    const token = getAuthToken()
    const userId = getUserId()

    if (!token || !userId) {
      dispatch({ type: 'SET_ERROR', payload: 'Not authenticated' })
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(updates),
      })

      if (response.ok) {
        dispatch({ type: 'UPDATE_TASK', payload: { id, updates } })
      } else {
        const error = await response.json()
        dispatch({ type: 'SET_ERROR', payload: error.detail || 'Failed to update task' })
      }
    } catch (error) {
      console.error('Error updating task:', error)
      dispatch({ type: 'SET_ERROR', payload: 'Failed to update task' })
    }
  }, [])

  // Delete task via API
  const deleteTask = useCallback(async (id: string) => {
    const token = getAuthToken()
    const userId = getUserId()

    if (!token || !userId) {
      dispatch({ type: 'SET_ERROR', payload: 'Not authenticated' })
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks/${id}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok || response.status === 204) {
        dispatch({ type: 'DELETE_TASK', payload: id })
      } else {
        const error = await response.json()
        dispatch({ type: 'SET_ERROR', payload: error.detail || 'Failed to delete task' })
      }
    } catch (error) {
      console.error('Error deleting task:', error)
      dispatch({ type: 'SET_ERROR', payload: 'Failed to delete task' })
    }
  }, [])

  // Toggle task completion via API
  const toggleComplete = useCallback(async (id: string) => {
    const task = state.tasks.find(t => t.id === id)
    if (!task) return

    const token = getAuthToken()
    const userId = getUserId()

    if (!token || !userId) {
      dispatch({ type: 'SET_ERROR', payload: 'Not authenticated' })
      return
    }

    // Optimistic update
    dispatch({ type: 'TOGGLE_COMPLETE', payload: id })

    try {
      const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ completed: !task.completed }),
      })

      if (!response.ok) {
        // Revert on failure
        dispatch({ type: 'TOGGLE_COMPLETE', payload: id })
        const error = await response.json()
        dispatch({ type: 'SET_ERROR', payload: error.detail || 'Failed to update task' })
      }
    } catch (error) {
      // Revert on failure
      dispatch({ type: 'TOGGLE_COMPLETE', payload: id })
      console.error('Error toggling task:', error)
      dispatch({ type: 'SET_ERROR', payload: 'Failed to update task' })
    }
  }, [state.tasks])

  // Fetch tasks on mount and when auth changes
  useEffect(() => {
    const token = getAuthToken()
    const userId = getUserId()
    if (token && userId) {
      fetchTasks()
    }
  }, [fetchTasks])

  // Listen for storage changes (login/logout)
  useEffect(() => {
    const handleStorageChange = () => {
      const token = getAuthToken()
      const userId = getUserId()
      if (token && userId) {
        fetchTasks()
      } else {
        dispatch({ type: 'SET_TASKS', payload: [] })
      }
    }

    window.addEventListener('storage', handleStorageChange)
    return () => window.removeEventListener('storage', handleStorageChange)
  }, [fetchTasks])

  // Listen for task modifications from chatbot
  useEffect(() => {
    const handleChatTaskModification = () => {
      fetchTasks()
    }

    window.addEventListener('tasks-modified-by-chat', handleChatTaskModification)
    return () => window.removeEventListener('tasks-modified-by-chat', handleChatTaskModification)
  }, [fetchTasks])

  return (
    <TaskContext.Provider value={{
      state,
      dispatch,
      fetchTasks,
      addTask,
      updateTask,
      deleteTask,
      toggleComplete
    }}>
      {children}
    </TaskContext.Provider>
  )
}

// Hook to access state
export function useTasks() {
  const context = useContext(TaskContext)
  if (!context) {
    throw new Error('useTasks must be used within TaskProvider')
  }
  return context.state
}

// Hook to access dispatch (for backwards compatibility)
export function useTaskActions() {
  const context = useContext(TaskContext)
  if (!context) {
    throw new Error('useTaskActions must be used within TaskProvider')
  }
  return context.dispatch
}

// Hook to access API actions
export function useTaskAPI() {
  const context = useContext(TaskContext)
  if (!context) {
    throw new Error('useTaskAPI must be used within TaskProvider')
  }
  return {
    fetchTasks: context.fetchTasks,
    addTask: context.addTask,
    updateTask: context.updateTask,
    deleteTask: context.deleteTask,
    toggleComplete: context.toggleComplete,
  }
}
