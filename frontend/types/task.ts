// Priority levels
export type TaskPriority = 'none' | 'low' | 'medium' | 'high' | 'urgent'

// Core task entity (Phase V: extended with priority, tags, due dates, recurrence)
export interface Task {
  id: string
  title: string
  description: string
  completed: boolean
  priority: TaskPriority
  tags: string[]
  dueDate: string | null
  isOverdue: boolean
  recurrenceRule: string | null
  recurrenceGroupId: string | null
  createdAt: Date
  updatedAt?: Date
}

// Paginated response from backend
export interface PaginatedTaskResponse {
  tasks: Task[]
  total: number
  limit: number
  offset: number
}

// Reminder entity
export interface Reminder {
  id: string
  taskId: string
  userId: string
  triggerAt: string
  status: 'pending' | 'triggered' | 'cancelled'
  createdAt: string
}

// Filter type for task display
export type FilterType = 'all' | 'active' | 'completed'

// Task query filters for API
export interface TaskFilters {
  q?: string
  completed?: boolean
  priority?: string
  tag?: string
  overdue?: boolean
  dueBefore?: string
  dueAfter?: string
  sortBy?: 'priority' | 'due_date' | 'created_at' | 'updated_at' | 'title'
  sortOrder?: 'asc' | 'desc'
  limit?: number
  offset?: number
}

// UI state for modals and loading
export interface UIState {
  activeFilter: FilterType
  modalOpen: boolean
  modalMode: 'add' | 'edit' | 'delete' | null
  editingTaskId: string | null
  isLoading: boolean
  error: string | null
}

// Global application state
export interface AppState {
  tasks: Task[]
  ui: UIState
}

// Reducer actions
export type TaskAction =
  | { type: 'SET_TASKS'; payload: Task[] }
  | { type: 'ADD_TASK'; payload: Task }
  | { type: 'UPDATE_TASK'; payload: { id: string; updates: Partial<Omit<Task, 'id' | 'createdAt'>> } }
  | { type: 'DELETE_TASK'; payload: string }
  | { type: 'TOGGLE_COMPLETE'; payload: string }
  | { type: 'SET_FILTER'; payload: FilterType }
  | { type: 'OPEN_MODAL'; payload: { mode: 'add' | 'edit' | 'delete'; taskId?: string } }
  | { type: 'CLOSE_MODAL' }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }

// Helper type for task form data (Phase V: extended)
export interface TaskFormData {
  title: string
  description?: string
  priority?: TaskPriority
  tags?: string[]
  dueDate?: string
  recurrenceRule?: string
}
