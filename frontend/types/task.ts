// Core task entity
export interface Task {
  id: string
  title: string
  description: string
  completed: boolean
  createdAt: Date
  updatedAt?: Date
}

// Filter type for task display
export type FilterType = 'all' | 'active' | 'completed'

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

// Helper type for task form data
export interface TaskFormData {
  title: string
  description?: string
}
