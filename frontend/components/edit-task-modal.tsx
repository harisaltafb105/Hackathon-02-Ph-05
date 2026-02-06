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
import { useTasks, useTaskActions, useTaskAPI } from '@/context/task-context'
import type { TaskFormData } from '@/types/task'

export function EditTaskModal() {
  const { tasks, ui } = useTasks()
  const dispatch = useTaskActions()
  const { updateTask } = useTaskAPI()
  const [isLoading, setIsLoading] = useState(false)

  const isOpen = ui.modalOpen && ui.modalMode === 'edit'

  // Find the task being edited
  const taskToEdit = tasks.find((task) => task.id === ui.editingTaskId)

  const handleSubmit = async (data: TaskFormData) => {
    if (!taskToEdit) return

    setIsLoading(true)

    // Update task via API
    await updateTask(taskToEdit.id, {
      title: data.title,
      description: data.description || '',
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
      <DialogContent>
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
            }}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            isLoading={isLoading}
          />
        </motion.div>
      </DialogContent>
    </Dialog>
  )
}
