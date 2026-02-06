# Data Model: Frontend-First Todo Web Application UI

**Feature**: 001-frontend-ui
**Date**: 2026-01-05
**Purpose**: Define data structures, state management, and type definitions for frontend application

## Overview

This data model defines the client-side data structures for a frontend-only Todo application. All data exists in component state (React Context) with no backend persistence. The model is designed to be "backend-ready" - easy to swap mocked local state for API calls in future phases.

## Core Entities

### Task

Represents a single todo item in the application.

**TypeScript Definition**:
```typescript
interface Task {
  id: string                    // UUID or timestamp-based unique identifier
  title: string                 // Required, 1-200 characters, user-facing task name
  description: string           // Optional, 0-1000 characters, additional details
  completed: boolean            // Completion status, defaults to false
  createdAt: Date               // Auto-generated timestamp for sorting
  updatedAt?: Date              // Optional, updated on edit operations
}
```

**Field Specifications**:

| Field | Type | Required | Validation | Default | Notes |
|-------|------|----------|------------|---------|-------|
| id | string | Yes | Non-empty, unique | Generated | UUID v4 or `Date.now()` + random suffix |
| title | string | Yes | 1-200 chars, trimmed | N/A | Cannot be only whitespace |
| description | string | No | 0-1000 chars | Empty string | Supports multiline text |
| completed | boolean | Yes | Boolean | false | Toggled via checkbox/button |
| createdAt | Date | Yes | Valid Date | Auto | ISO 8601 format for serialization |
| updatedAt | Date | No | Valid Date | undefined | Set on edit, not on toggle |

**State Transitions**:
```
[Created] → completed: false, createdAt: now()
[Updated] → updatedAt: now(), other fields modified
[Completed] → completed: true (no updatedAt change)
[Uncompleted] → completed: false (no updatedAt change)
[Deleted] → removed from state
```

**Validation Rules**:
1. Title cannot be empty after trimming whitespace
2. Title length between 1-200 characters after trimming
3. Description max 1000 characters (no trimming)
4. ID must be unique across all tasks
5. Completed must be boolean (no nullish values)

**Example Instances**:
```typescript
// Minimal task
{
  id: "123e4567-e89b-12d3-a456-426614174000",
  title: "Buy groceries",
  description: "",
  completed: false,
  createdAt: new Date("2026-01-05T10:30:00Z")
}

// Complete task with description
{
  id: "987fcdeb-51a2-43f7-b8c9-123456789abc",
  title: "Finish project documentation",
  description: "Include API reference and user guide\nReview with team before Friday",
  completed: true,
  createdAt: new Date("2026-01-03T09:00:00Z"),
  updatedAt: new Date("2026-01-04T14:30:00Z")
}
```

---

### FilterType

Represents the current filter applied to the task list view.

**TypeScript Definition**:
```typescript
type FilterType = 'all' | 'active' | 'completed'
```

**Filter Behavior**:

| Filter | Description | Tasks Shown | Use Case |
|--------|-------------|-------------|----------|
| `all` | No filtering | All tasks regardless of status | Default view, overview |
| `active` | Only pending tasks | Tasks where `completed === false` | Focus on work to do |
| `completed` | Only finished tasks | Tasks where `completed === true` | Review accomplishments |

**State Transitions**:
```
User clicks "All" tab → filter: 'all'
User clicks "Active" tab → filter: 'active'
User clicks "Completed" tab → filter: 'completed'
```

---

### UIState

Represents transient UI state for modals, loading, and user interactions.

**TypeScript Definition**:
```typescript
interface UIState {
  activeModal: ModalType | null
  isLoading: boolean
  selectedTaskId: string | null
  error: string | null
}

type ModalType = 'add-task' | 'edit-task' | 'delete-confirm'
```

**Field Specifications**:

| Field | Type | Purpose | Default | Notes |
|-------|------|---------|---------|-------|
| activeModal | ModalType \| null | Which modal is currently open | null | Only one modal open at a time |
| isLoading | boolean | Simulate async operations | false | Shows skeleton/spinner |
| selectedTaskId | string \| null | Task being edited/deleted | null | Used with edit/delete modals |
| error | string \| null | Error message to display | null | Future: API error handling |

**Modal State Transitions**:
```
Click "Add Task" → activeModal: 'add-task', selectedTaskId: null
Click "Edit" on task → activeModal: 'edit-task', selectedTaskId: task.id
Click "Delete" on task → activeModal: 'delete-confirm', selectedTaskId: task.id
Close modal / Cancel → activeModal: null, selectedTaskId: null
Submit success → activeModal: null, selectedTaskId: null, isLoading: false
```

---

## Application State Structure

### Global State (React Context)

**TypeScript Definition**:
```typescript
interface AppState {
  tasks: Task[]
  filter: FilterType
  ui: UIState
}
```

**Initial State**:
```typescript
const initialState: AppState = {
  tasks: [
    // 5-10 mocked tasks for demonstration
    { id: "1", title: "Welcome to your Todo app", description: "This is a sample task", completed: false, createdAt: new Date() },
    // ... more mocked tasks
  ],
  filter: 'all',
  ui: {
    activeModal: null,
    isLoading: false,
    selectedTaskId: null,
    error: null
  }
}
```

**State Access Pattern**:
```typescript
// Provider at app root
<TaskProvider initialTasks={mockedTasks}>
  <App />
</TaskProvider>

// Access in components
const { tasks, filter, ui } = useTasks()
const { addTask, updateTask, deleteTask, toggleComplete, setFilter } = useTaskActions()
```

---

## State Management Architecture

### Reducer Actions

**TypeScript Definitions**:
```typescript
type TaskAction =
  // Task CRUD
  | { type: 'ADD_TASK'; payload: Omit<Task, 'id' | 'createdAt'> }
  | { type: 'UPDATE_TASK'; payload: { id: string; updates: Partial<Omit<Task, 'id' | 'createdAt'>> } }
  | { type: 'DELETE_TASK'; payload: string }
  | { type: 'TOGGLE_COMPLETE'; payload: string }

  // Filtering
  | { type: 'SET_FILTER'; payload: FilterType }

  // UI State
  | { type: 'OPEN_MODAL'; payload: { modal: ModalType; taskId?: string } }
  | { type: 'CLOSE_MODAL' }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
```

**Reducer Logic** (pseudocode):
```typescript
function taskReducer(state: AppState, action: TaskAction): AppState {
  switch (action.type) {
    case 'ADD_TASK':
      const newTask: Task = {
        ...action.payload,
        id: generateId(),
        createdAt: new Date(),
        completed: false
      }
      return {
        ...state,
        tasks: [...state.tasks, newTask]
      }

    case 'UPDATE_TASK':
      return {
        ...state,
        tasks: state.tasks.map(task =>
          task.id === action.payload.id
            ? { ...task, ...action.payload.updates, updatedAt: new Date() }
            : task
        )
      }

    case 'DELETE_TASK':
      return {
        ...state,
        tasks: state.tasks.filter(task => task.id !== action.payload)
      }

    case 'TOGGLE_COMPLETE':
      return {
        ...state,
        tasks: state.tasks.map(task =>
          task.id === action.payload
            ? { ...task, completed: !task.completed }
            : task
        )
      }

    case 'SET_FILTER':
      return {
        ...state,
        filter: action.payload
      }

    case 'OPEN_MODAL':
      return {
        ...state,
        ui: {
          ...state.ui,
          activeModal: action.payload.modal,
          selectedTaskId: action.payload.taskId || null
        }
      }

    case 'CLOSE_MODAL':
      return {
        ...state,
        ui: {
          ...state.ui,
          activeModal: null,
          selectedTaskId: null
        }
      }

    case 'SET_LOADING':
      return {
        ...state,
        ui: { ...state.ui, isLoading: action.payload }
      }

    case 'SET_ERROR':
      return {
        ...state,
        ui: { ...state.ui, error: action.payload }
      }

    default:
      return state
  }
}
```

---

## Derived State (Computed)

### Filtered Tasks

**Computation Logic**:
```typescript
function useFilteredTasks(): Task[] {
  const { tasks, filter } = useTasks()

  return useMemo(() => {
    switch (filter) {
      case 'all':
        return tasks
      case 'active':
        return tasks.filter(task => !task.completed)
      case 'completed':
        return tasks.filter(task => task.completed)
      default:
        return tasks
    }
  }, [tasks, filter])
}
```

**Memoization**: Uses `useMemo` to avoid recalculating on every render. Recomputes only when `tasks` or `filter` change.

### Task Counts

**Computation Logic**:
```typescript
function useTaskCounts() {
  const { tasks } = useTasks()

  return useMemo(() => ({
    total: tasks.length,
    active: tasks.filter(t => !t.completed).length,
    completed: tasks.filter(t => t.completed).length
  }), [tasks])
}
```

**Usage**: Display counts in filter tabs ("Active (5)", "Completed (3)")

---

## Async Simulation

Since this is frontend-only with no real backend, async operations are simulated to demonstrate loading states.

**Simulation Pattern**:
```typescript
async function simulateAsyncOperation<T>(operation: () => T, delay: number = 500): Promise<T> {
  await new Promise(resolve => setTimeout(resolve, delay))
  return operation()
}

// Usage in action handlers
async function handleAddTask(taskData: Omit<Task, 'id' | 'createdAt'>) {
  dispatch({ type: 'SET_LOADING', payload: true })

  await simulateAsyncOperation(() => {
    dispatch({ type: 'ADD_TASK', payload: taskData })
  }, 500)

  dispatch({ type: 'SET_LOADING', payload: false })
  dispatch({ type: 'CLOSE_MODAL' })
}
```

**Delay Guidelines**:
- **Add/Edit/Delete**: 500ms (visible loading state per spec FR-009)
- **Toggle complete**: 0ms (instant feedback, no loading state)
- **Filter change**: 0ms (instant, but animated transition)

---

## Validation Logic

### Client-Side Validation

**Validation Schema (Zod)**:
```typescript
import { z } from 'zod'

const taskSchema = z.object({
  title: z.string()
    .min(1, "Title is required")
    .max(200, "Title must be 200 characters or less")
    .trim()
    .refine(val => val.length > 0, "Title cannot be only whitespace"),

  description: z.string()
    .max(1000, "Description must be 1000 characters or less")
    .optional()
    .default("")
})

type TaskFormData = z.infer<typeof taskSchema>
```

**Validation Timing**:
- **On blur**: Check field after user leaves it
- **On submit**: Validate entire form before dispatch
- **Real-time**: Show character count for description (not blocking)

**Error Display**:
- Inline below field: "Title is required"
- Red border on input field
- Icon indicator (optional)
- Accessible via `aria-describedby`

---

## Type Exports

**File: `types/task.ts`**
```typescript
export interface Task {
  id: string
  title: string
  description: string
  completed: boolean
  createdAt: Date
  updatedAt?: Date
}

export type FilterType = 'all' | 'active' | 'completed'

export interface UIState {
  activeModal: ModalType | null
  isLoading: boolean
  selectedTaskId: string | null
  error: string | null
}

export type ModalType = 'add-task' | 'edit-task' | 'delete-confirm'

export interface AppState {
  tasks: Task[]
  filter: FilterType
  ui: UIState
}

export type TaskAction =
  | { type: 'ADD_TASK'; payload: Omit<Task, 'id' | 'createdAt'> }
  | { type: 'UPDATE_TASK'; payload: { id: string; updates: Partial<Omit<Task, 'id' | 'createdAt'>> } }
  | { type: 'DELETE_TASK'; payload: string }
  | { type: 'TOGGLE_COMPLETE'; payload: string }
  | { type: 'SET_FILTER'; payload: FilterType }
  | { type: 'OPEN_MODAL'; payload: { modal: ModalType; taskId?: string } }
  | { type: 'CLOSE_MODAL' }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
```

---

## Mocked Data

### Initial Tasks (Development)

**File: `lib/mock-data.ts`**
```typescript
export const mockedTasks: Task[] = [
  {
    id: "1",
    title: "Welcome to your Todo app! 🎉",
    description: "This is a sample task to help you get started. Try marking it complete!",
    completed: false,
    createdAt: new Date("2026-01-05T08:00:00Z")
  },
  {
    id: "2",
    title: "Add your first real task",
    description: "Click the Add Task button to create your own todo item",
    completed: false,
    createdAt: new Date("2026-01-05T08:05:00Z")
  },
  {
    id: "3",
    title: "Try filtering tasks",
    description: "Use the All / Active / Completed tabs to focus your view",
    completed: false,
    createdAt: new Date("2026-01-05T08:10:00Z")
  },
  {
    id: "4",
    title: "Edit an existing task",
    description: "Hover over a task and click Edit to modify it",
    completed: false,
    createdAt: new Date("2026-01-05T08:15:00Z")
  },
  {
    id: "5",
    title: "Explore the responsive design",
    description: "Resize your browser to see how the layout adapts",
    completed: false,
    createdAt: new Date("2026-01-05T08:20:00Z")
  },
  {
    id: "6",
    title: "Sample completed task",
    description: "This task is already done to demonstrate the completed state",
    completed: true,
    createdAt: new Date("2026-01-04T10:00:00Z"),
    updatedAt: new Date("2026-01-04T15:30:00Z")
  }
]
```

---

## Summary

**Data Model Characteristics**:
- ✅ Type-safe with TypeScript
- ✅ Immutable state updates
- ✅ Centralized state management (Context + Reducer)
- ✅ Derived state computed with memoization
- ✅ Client-side validation with Zod
- ✅ Async simulation for loading states
- ✅ Backend-ready architecture (easy to swap mocked state for API calls)

**Next Steps**:
- Define UI contracts (component props) in Phase 1 contracts
- Implement context provider and hooks
- Create TypeScript type definitions file
- Build components using these data structures
