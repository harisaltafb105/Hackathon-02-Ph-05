import { useMemo } from 'react'
import { useTasks } from '@/context/task-context'
import type { Task, FilterType } from '@/types/task'

/**
 * Hook to get filtered tasks based on active filter
 * Returns memoized filtered task list
 */
export function useFilteredTasks(): Task[] {
  const { tasks, ui } = useTasks()
  const { activeFilter } = ui

  return useMemo(() => {
    switch (activeFilter) {
      case 'active':
        return tasks.filter((task) => !task.completed)
      case 'completed':
        return tasks.filter((task) => task.completed)
      case 'all':
      default:
        return tasks
    }
  }, [tasks, activeFilter])
}
