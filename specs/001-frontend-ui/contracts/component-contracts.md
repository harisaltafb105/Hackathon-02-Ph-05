# Component Contracts: Frontend Todo Application

**Feature**: 001-frontend-ui
**Date**: 2026-01-05
**Purpose**: Define component interfaces, props, and interaction contracts

## Overview

This document specifies the interface contracts for all React components in the Todo application. These contracts serve as the "API" between components, ensuring consistent data flow and behavior.

---

## Atomic Components (shadcn/ui)

### Button

**Source**: `components/ui/button.tsx` (shadcn/ui)

**Interface**:
```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link'
  size?: 'default' | 'sm' | 'lg' | 'icon'
  asChild?: boolean
}
```

**Variants**:
- `default`: Primary actions (e.g., "Add Task", "Save")
- `destructive`: Dangerous actions (e.g., "Delete")
- `outline`: Secondary actions (e.g., "Cancel")
- `ghost`: Tertiary actions (e.g., icon buttons)

**Usage Examples**:
```tsx
<Button variant="default" size="lg">Add Task</Button>
<Button variant="destructive" size="sm">Delete</Button>
<Button variant="outline">Cancel</Button>
```

---

### Card

**Source**: `components/ui/card.tsx` (shadcn/ui)

**Interface**:
```typescript
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {}

// Subcomponents
CardHeader, CardTitle, CardDescription, CardContent, CardFooter
```

**Usage Pattern**:
```tsx
<Card>
  <CardHeader>
    <CardTitle>Task Title</CardTitle>
    <CardDescription>Optional metadata</CardDescription>
  </CardHeader>
  <CardContent>Main content</CardContent>
  <CardFooter>Actions</CardFooter>
</Card>
```

---

### Dialog

**Source**: `components/ui/dialog.tsx` (shadcn/ui)

**Interface**:
```typescript
interface DialogProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  children: React.ReactNode
}

// Subcomponents
DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter
```

**Usage Pattern**:
```tsx
<Dialog open={isOpen} onOpenChange={setIsOpen}>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Add Task</DialogTitle>
      <DialogDescription>Create a new todo item</DialogDescription>
    </DialogHeader>
    {/* Form content */}
    <DialogFooter>
      <Button onClick={handleCancel}>Cancel</Button>
      <Button onClick={handleSubmit}>Save</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

---

### Input

**Source**: `components/ui/input.tsx` (shadcn/ui)

**Interface**:
```typescript
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}
```

**Usage**:
```tsx
<Input
  type="text"
  placeholder="Enter task title..."
  value={title}
  onChange={(e) => setTitle(e.target.value)}
  aria-invalid={hasError}
  aria-describedby={hasError ? "title-error" : undefined}
/>
```

---

### Checkbox

**Source**: `components/ui/checkbox.tsx` (shadcn/ui)

**Interface**:
```typescript
interface CheckboxProps {
  checked?: boolean
  onCheckedChange?: (checked: boolean) => void
  disabled?: boolean
  id?: string
  name?: string
}
```

**Usage**:
```tsx
<Checkbox
  checked={task.completed}
  onCheckedChange={() => toggleComplete(task.id)}
  aria-label={`Mark "${task.title}" as ${task.completed ? 'incomplete' : 'complete'}`}
/>
```

---

### Tabs

**Source**: `components/ui/tabs.tsx` (shadcn/ui)

**Interface**:
```typescript
interface TabsProps {
  defaultValue?: string
  value?: string
  onValueChange?: (value: string) => void
  children: React.ReactNode
}

// Subcomponents
TabsList, TabsTrigger, TabsContent
```

**Usage Pattern**:
```tsx
<Tabs value={filter} onValueChange={(v) => setFilter(v as FilterType)}>
  <TabsList>
    <TabsTrigger value="all">All</TabsTrigger>
    <TabsTrigger value="active">Active</TabsTrigger>
    <TabsTrigger value="completed">Completed</TabsTrigger>
  </TabsList>
</Tabs>
```

---

### Skeleton

**Source**: `components/ui/skeleton.tsx` (shadcn/ui)

**Interface**:
```typescript
interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {}
```

**Usage**:
```tsx
<Skeleton className="h-24 w-full rounded-lg" />
```

---

## Molecule Components

### TaskCard

**Purpose**: Display a single task with completion toggle and action buttons

**File**: `components/task-card.tsx`

**Interface**:
```typescript
interface TaskCardProps {
  task: Task
  onToggleComplete: (taskId: string) => void
  onEdit: (taskId: string) => void
  onDelete: (taskId: string) => void
}
```

**Behavior**:
- Display task title (required), description (if present), completion status
- Checkbox on left for completion toggle
- Hover shows action buttons (Edit, Delete) on right
- Click checkbox triggers `onToggleComplete` with animation
- Click Edit opens edit modal via `onEdit`
- Click Delete opens delete confirmation via `onDelete`
- Visual state changes: completed tasks have strikethrough, muted colors, check icon

**Accessibility**:
- Checkbox has aria-label with task title
- Edit/Delete buttons have aria-labels
- Focus visible on all interactive elements
- Keyboard accessible (Tab, Enter, Space)

**Animation**:
- Completion toggle: scale + opacity transition (200ms)
- Hover state: smooth button fade-in (150ms)
- Layout animation when task order changes

**Example**:
```tsx
<TaskCard
  task={task}
  onToggleComplete={handleToggleComplete}
  onEdit={handleEdit}
  onDelete={handleDelete}
/>
```

---

### TaskForm

**Purpose**: Form for adding or editing task details

**File**: `components/task-form.tsx`

**Interface**:
```typescript
interface TaskFormProps {
  mode: 'add' | 'edit'
  initialData?: Partial<Task>
  onSubmit: (data: { title: string; description: string }) => void
  onCancel: () => void
  isLoading?: boolean
}
```

**Behavior**:
- Two input fields: title (required), description (optional)
- Inline validation on blur and submit
- Character count for description (max 1000)
- Loading state disables inputs and shows spinner on submit button
- Enter key submits form (if title valid)
- Escape key cancels form

**Validation**:
- Title: 1-200 characters, cannot be only whitespace
- Description: 0-1000 characters
- Inline error messages below fields
- Red border on invalid fields

**Accessibility**:
- Form has aria-labelledby pointing to modal title
- Inputs have associated labels
- Error messages connected via aria-describedby
- Focus trapped in form (modal context)

**Example**:
```tsx
<TaskForm
  mode="add"
  onSubmit={handleSubmit}
  onCancel={handleCancel}
  isLoading={isSubmitting}
/>

<TaskForm
  mode="edit"
  initialData={{ title: task.title, description: task.description }}
  onSubmit={handleUpdate}
  onCancel={handleCancel}
/>
```

---

### FilterTabs

**Purpose**: Filter controls to show All/Active/Completed tasks

**File**: `components/filter-tabs.tsx`

**Interface**:
```typescript
interface FilterTabsProps {
  activeFilter: FilterType
  onFilterChange: (filter: FilterType) => void
  counts: {
    all: number
    active: number
    completed: number
  }
}
```

**Behavior**:
- Three tabs: All, Active, Completed
- Show count for each filter (e.g., "Active (5)")
- Active tab highlighted with accent color
- Click tab triggers `onFilterChange` with smooth transition

**Accessibility**:
- Tabs have role="tablist"
- Each tab has role="tab"
- Active tab has aria-selected="true"
- Keyboard navigation (Arrow keys)

**Example**:
```tsx
<FilterTabs
  activeFilter={filter}
  onFilterChange={setFilter}
  counts={{ all: 10, active: 5, completed: 5 }}
/>
```

---

### EmptyState

**Purpose**: Display when no tasks match current filter

**File**: `components/empty-state.tsx`

**Interface**:
```typescript
interface EmptyStateProps {
  filter: FilterType
  onAddTask: () => void
}
```

**Behavior**:
- Display icon (Lucide CheckSquare or Clipboard)
- Contextual message based on filter:
  - `all`: "No tasks yet. Add your first task to get started!"
  - `active`: "All tasks completed! 🎉"
  - `completed`: "No completed tasks yet. Get started on your todos!"
- Primary CTA button ("Add Task" for all/active, optional for completed)

**Accessibility**:
- Icon has aria-hidden="true"
- Message in paragraph with good contrast
- CTA button clearly labeled

**Example**:
```tsx
<EmptyState
  filter="all"
  onAddTask={() => dispatch({ type: 'OPEN_MODAL', payload: { modal: 'add-task' } })}
/>
```

---

### TaskListSkeleton

**Purpose**: Loading state placeholder matching task list layout

**File**: `components/task-list-skeleton.tsx`

**Interface**:
```typescript
interface TaskListSkeletonProps {
  count?: number
}
```

**Behavior**:
- Render `count` skeleton task cards (default 5)
- Match TaskCard dimensions and layout
- Pulse animation via shadcn/ui Skeleton component

**Accessibility**:
- Container has aria-busy="true"
- aria-label="Loading tasks"

**Example**:
```tsx
{isLoading ? (
  <TaskListSkeleton count={5} />
) : (
  <TaskList tasks={filteredTasks} />
)}
```

---

## Organism Components

### TaskList

**Purpose**: Render filtered list of tasks with animations

**File**: `components/task-list.tsx`

**Interface**:
```typescript
interface TaskListProps {
  tasks: Task[]
  onToggleComplete: (taskId: string) => void
  onEdit: (taskId: string) => void
  onDelete: (taskId: string) => void
}
```

**Behavior**:
- Map over tasks, render TaskCard for each
- Wrap in Framer Motion AnimatePresence for enter/exit animations
- Apply layout animations for reordering
- Handle empty state (no tasks)

**Animation**:
- Task entry: fade + slide from below (200ms)
- Task exit: fade + slide to left (200ms)
- Layout shift: smooth position transition (300ms)

**Accessibility**:
- List has role="list"
- Each card has role="listitem"
- Announce task count to screen readers

**Example**:
```tsx
<TaskList
  tasks={filteredTasks}
  onToggleComplete={handleToggleComplete}
  onEdit={handleEditTask}
  onDelete={handleDeleteTask}
/>
```

---

### AddTaskModal

**Purpose**: Modal dialog for adding new tasks

**File**: `components/add-task-modal.tsx`

**Interface**:
```typescript
interface AddTaskModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: { title: string; description: string }) => Promise<void>
}
```

**Behavior**:
- shadcn/ui Dialog wrapper
- TaskForm in content area
- Close on backdrop click or Escape key
- Close on successful submit
- Show loading state during simulated async operation

**Focus Management**:
- Focus title input on open
- Return focus to "Add Task" button on close

**Animation**:
- Backdrop fade in (200ms)
- Content scale + slide from below (250ms)

**Example**:
```tsx
<AddTaskModal
  isOpen={ui.activeModal === 'add-task'}
  onClose={handleCloseModal}
  onSubmit={handleAddTask}
/>
```

---

### EditTaskModal

**Purpose**: Modal dialog for editing existing tasks

**File**: `components/edit-task-modal.tsx`

**Interface**:
```typescript
interface EditTaskModalProps {
  isOpen: boolean
  task: Task | null
  onClose: () => void
  onSubmit: (taskId: string, updates: { title: string; description: string }) => Promise<void>
}
```

**Behavior**:
- Similar to AddTaskModal but with existing task data
- Pre-fill form with current task values
- Save updates on submit
- Close on cancel or successful save

**Validation**:
- Same as AddTaskModal (title required, length limits)

**Example**:
```tsx
<EditTaskModal
  isOpen={ui.activeModal === 'edit-task'}
  task={tasks.find(t => t.id === ui.selectedTaskId) || null}
  onClose={handleCloseModal}
  onSubmit={handleUpdateTask}
/>
```

---

### DeleteConfirmDialog

**Purpose**: Confirmation dialog before deleting task

**File**: `components/delete-confirm-dialog.tsx`

**Interface**:
```typescript
interface DeleteConfirmDialogProps {
  isOpen: boolean
  task: Task | null
  onClose: () => void
  onConfirm: (taskId: string) => Promise<void>
}
```

**Behavior**:
- Show task title in confirmation message
- Two buttons: Cancel (outline) and Delete (destructive)
- Close on Cancel or backdrop click
- Execute delete on Confirm with loading state
- Close after successful deletion

**Accessibility**:
- Dialog has role="alertdialog"
- Focus Delete button by default (dangerous action)
- Escape key cancels

**Example**:
```tsx
<DeleteConfirmDialog
  isOpen={ui.activeModal === 'delete-confirm'}
  task={tasks.find(t => t.id === ui.selectedTaskId) || null}
  onClose={handleCloseModal}
  onConfirm={handleDeleteTask}
/>
```

---

## Page Components

### HomePage

**Purpose**: Main application page with task list and controls

**File**: `app/page.tsx`

**Interface**:
```typescript
// No props - root page component
export default function HomePage() {
  // Uses context hooks
  const { tasks, filter, ui } = useTasks()
  const actions = useTaskActions()

  return (/* JSX */)
}
```

**Layout Structure**:
```
<main>
  <header>
    <h1>My Tasks</h1>
    <FilterTabs />
    <Button>Add Task</Button>
  </header>

  <section>
    {isLoading ? (
      <TaskListSkeleton />
    ) : filteredTasks.length === 0 ? (
      <EmptyState />
    ) : (
      <TaskList />
    )}
  </section>

  <AddTaskModal />
  <EditTaskModal />
  <DeleteConfirmDialog />
</main>
```

**Responsive Behavior**:
- Mobile: Stacked layout, full-width cards
- Desktop: Max-width container, potentially multi-column

---

## Context Hooks

### useTasks

**Purpose**: Access task state from context

**File**: `context/task-context.tsx`

**Interface**:
```typescript
function useTasks(): {
  tasks: Task[]
  filter: FilterType
  ui: UIState
}
```

**Usage**:
```tsx
const { tasks, filter, ui } = useTasks()
```

---

### useTaskActions

**Purpose**: Access action dispatchers

**File**: `context/task-context.tsx`

**Interface**:
```typescript
function useTaskActions(): {
  addTask: (data: Omit<Task, 'id' | 'createdAt'>) => Promise<void>
  updateTask: (id: string, updates: Partial<Task>) => Promise<void>
  deleteTask: (id: string) => Promise<void>
  toggleComplete: (id: string) => void
  setFilter: (filter: FilterType) => void
  openModal: (modal: ModalType, taskId?: string) => void
  closeModal: () => void
}
```

**Usage**:
```tsx
const { addTask, toggleComplete, openModal } = useTaskActions()

await addTask({ title: "New task", description: "" })
toggleComplete(taskId)
openModal('edit-task', taskId)
```

---

### useFilteredTasks

**Purpose**: Get tasks filtered by current filter

**File**: `hooks/use-filtered-tasks.ts`

**Interface**:
```typescript
function useFilteredTasks(): Task[]
```

**Usage**:
```tsx
const filteredTasks = useFilteredTasks()
```

---

### useTaskCounts

**Purpose**: Get task counts for filter tabs

**File**: `hooks/use-task-counts.ts`

**Interface**:
```typescript
function useTaskCounts(): {
  all: number
  active: number
  completed: number
}
```

**Usage**:
```tsx
const counts = useTaskCounts()
// { all: 10, active: 5, completed: 5 }
```

---

## Summary

**Component Hierarchy**:
```
App (TaskProvider)
└── HomePage
    ├── Header
    │   ├── FilterTabs
    │   └── Button (Add Task)
    ├── TaskList (or EmptyState or Skeleton)
    │   └── TaskCard (multiple)
    ├── AddTaskModal
    │   └── TaskForm
    ├── EditTaskModal
    │   └── TaskForm
    └── DeleteConfirmDialog
```

**Data Flow**:
```
Context (state) → Hooks (selectors) → Components (UI)
User interactions → Action handlers → Dispatch → Reducer → Context (new state)
```

**Key Principles**:
- Props are type-safe with TypeScript
- Components are composable (atomic design)
- State flows down, actions flow up
- Accessibility built-in at every level
- Animations consistent across components
