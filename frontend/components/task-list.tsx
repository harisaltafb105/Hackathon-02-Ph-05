'use client'

import { AnimatePresence, motion } from 'framer-motion'
import { TaskCard } from '@/components/task-card'
import { EmptyState } from '@/components/empty-state'
import { useFilteredTasks } from '@/hooks/use-filtered-tasks'
import { useTasks, useTaskActions, useTaskAPI } from '@/context/task-context'

export function TaskList() {
  const filteredTasks = useFilteredTasks()
  const { ui } = useTasks()
  const dispatch = useTaskActions()
  const { toggleComplete } = useTaskAPI()

  const handleToggleComplete = (taskId: string) => {
    toggleComplete(taskId)
  }

  const handleEdit = (taskId: string) => {
    dispatch({ type: 'OPEN_MODAL', payload: { mode: 'edit', taskId } })
  }

  const handleDelete = (taskId: string) => {
    dispatch({ type: 'OPEN_MODAL', payload: { mode: 'delete', taskId } })
  }

  if (filteredTasks.length === 0) {
    return <EmptyState filter={ui.activeFilter} />
  }

  return (
    <motion.div
      layout
      className="space-y-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <AnimatePresence mode="popLayout">
        {filteredTasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            onToggleComplete={handleToggleComplete}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        ))}
      </AnimatePresence>
    </motion.div>
  )
}
