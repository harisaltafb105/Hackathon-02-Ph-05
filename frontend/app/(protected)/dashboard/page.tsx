/**
 * Dashboard Page (Protected)
 *
 * Main task management page for authenticated users.
 * Moved from root page.tsx to protected route group.
 *
 * Feature: 002-frontend-auth
 * Task: T027 (US3)
 */

'use client'

import { Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { FilterTabs } from '@/components/filter-tabs'
import { TaskList } from '@/components/task-list'
import { TaskListSkeleton } from '@/components/task-list-skeleton'
import { AddTaskModal } from '@/components/add-task-modal'
import { EditTaskModal } from '@/components/edit-task-modal'
import { DeleteConfirmDialog } from '@/components/delete-confirm-dialog'
import { useTasks } from '@/context/task-context'
import { useTaskActions } from '@/context/task-context'

export default function DashboardPage() {
  const { ui } = useTasks()
  const dispatch = useTaskActions()

  const handleAddTask = () => {
    dispatch({ type: 'OPEN_MODAL', payload: { mode: 'add' } })
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <header className="mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold text-foreground">
              My Tasks
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              Organize your work and life
            </p>
          </div>
          <Button
            onClick={handleAddTask}
            size="lg"
            className="w-full sm:w-auto"
            aria-label="Add new task"
          >
            <Plus className="h-5 w-5 mr-2" />
            Add Task
          </Button>
        </div>
        <Separator className="mb-6" />
        <FilterTabs />
      </header>

      {/* Task List */}
      <main>
        {ui.isLoading ? (
          <TaskListSkeleton />
        ) : (
          <TaskList />
        )}
      </main>

      {/* Add Task Modal */}
      <AddTaskModal />

      {/* Edit Task Modal */}
      <EditTaskModal />

      {/* Delete Confirm Dialog */}
      <DeleteConfirmDialog />
    </div>
  )
}
