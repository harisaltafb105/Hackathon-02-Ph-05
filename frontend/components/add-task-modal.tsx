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

export function AddTaskModal() {
  const { ui } = useTasks()
  const dispatch = useTaskActions()
  const { addTask } = useTaskAPI()
  const [isLoading, setIsLoading] = useState(false)

  const isOpen = ui.modalOpen && ui.modalMode === 'add'

  const handleSubmit = async (data: TaskFormData) => {
    setIsLoading(true)

    // Add task via API
    await addTask(data.title, data.description)

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
            <DialogTitle>Add New Task</DialogTitle>
            <DialogDescription>
              Create a new task to organize your work. Fill in the details below.
            </DialogDescription>
          </DialogHeader>
          <TaskForm
            mode="add"
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            isLoading={isLoading}
          />
        </motion.div>
      </DialogContent>
    </Dialog>
  )
}
