'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { TaskForm } from '@/components/task-form'
import { ReminderSection } from '@/components/reminder-section'
import { useTasks, useTaskActions, useTaskAPI } from '@/context/task-context'
import type { TaskFormData } from '@/types/task'

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

export function EditTaskModal() {
  const { tasks, ui } = useTasks()
  const dispatch = useTaskActions()
  const { updateTask } = useTaskAPI()
  const [isLoading, setIsLoading] = useState(false)

  const isOpen = ui.modalOpen && ui.modalMode === 'edit'

  // Find the task being edited
  const taskToEdit = tasks.find((task) => task.id === ui.editingTaskId)
  const userId = getUserId()

  const handleSubmit = async (data: TaskFormData) => {
    if (!taskToEdit) return

    setIsLoading(true)

    // Update task via API (Phase V: all fields)
    await updateTask(taskToEdit.id, {
      title: data.title,
      description: data.description || '',
      priority: data.priority,
      tags: data.tags,
      dueDate: data.dueDate,
      recurrenceRule: data.recurrenceRule,
    })

    setIsLoading(false)

    // Close modal
    dispatch({ type: 'CLOSE_MODAL' })
  }

  const handleCancel = () => {
    dispatch({ type: 'CLOSE_MODAL' })
  }

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      dispatch({ type: 'CLOSE_MODAL' })
    }
  }

  // Don't render if no task to edit
  if (!taskToEdit) return null

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogContent className="max-h-[85vh] overflow-y-auto">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ duration: 0.2, ease: 'easeOut' }}
        >
          <DialogHeader>
            <DialogTitle>Edit Task</DialogTitle>
            <DialogDescription>
              Update the details of your task below.
            </DialogDescription>
          </DialogHeader>
          <TaskForm
            mode="edit"
            initialData={{
              title: taskToEdit.title,
              description: taskToEdit.description,
              priority: taskToEdit.priority,
              tags: taskToEdit.tags,
              dueDate: taskToEdit.dueDate || undefined,
              recurrenceRule: taskToEdit.recurrenceRule || undefined,
            }}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            isLoading={isLoading}
          />
          {/* Phase V: Reminder management section */}
          {userId && (
            <ReminderSection
              taskId={taskToEdit.id}
              userId={userId}
              hasDueDate={!!taskToEdit.dueDate}
            />
          )}
        </motion.div>
      </DialogContent>
    </Dialog>
  )
}
