'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertTriangle, Loader2 } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { useTasks, useTaskActions, useTaskAPI } from '@/context/task-context'

export function DeleteConfirmDialog() {
  const { tasks, ui } = useTasks()
  const dispatch = useTaskActions()
  const { deleteTask } = useTaskAPI()
  const [isLoading, setIsLoading] = useState(false)

  const isOpen = ui.modalOpen && ui.modalMode === 'delete'

  // Find the task to delete
  const taskToDelete = tasks.find((task) => task.id === ui.editingTaskId)

  const handleConfirm = async () => {
    if (!taskToDelete) return

    setIsLoading(true)

    // Delete task via API
    await deleteTask(taskToDelete.id)

    setIsLoading(false)

    // Close dialog
    dispatch({ type: 'CLOSE_MODAL' })
  }

  const handleCancel = () => {
    dispatch({ type: 'CLOSE_MODAL' })
  }

  const handleOpenChange = (open: boolean) => {
    if (!open && !isLoading) {
      dispatch({ type: 'CLOSE_MODAL' })
    }
  }

  // Don't render if no task to delete
  if (!taskToDelete) return null

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogContent role="alertdialog">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ duration: 0.2, ease: 'easeOut' }}
        >
          <DialogHeader>
            <div className="flex items-center gap-3">
              <div className="rounded-full bg-destructive/10 p-2">
                <AlertTriangle className="h-5 w-5 text-destructive" />
              </div>
              <DialogTitle>Delete Task</DialogTitle>
            </div>
            <DialogDescription className="pt-2">
              Are you sure you want to delete{' '}
              <span className="font-semibold text-foreground">
                "{taskToDelete.title}"
              </span>
              ? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex-col-reverse sm:flex-row gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={handleCancel}
              disabled={isLoading}
              className="w-full sm:w-auto"
            >
              Cancel
            </Button>
            <Button
              type="button"
              variant="destructive"
              onClick={handleConfirm}
              disabled={isLoading}
              className="w-full sm:w-auto"
              autoFocus
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                'Delete Task'
              )}
            </Button>
          </DialogFooter>
        </motion.div>
      </DialogContent>
    </Dialog>
  )
}
