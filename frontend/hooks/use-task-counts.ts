import { useMemo } from 'react'
import { useTasks } from '@/context/task-context'

/**
 * Hook to get task counts by filter type
 * Returns memoized counts for all, active, and completed tasks
 */
export function useTaskCounts() {
  const { tasks } = useTasks()

  return useMemo(() => {
    const all = tasks.length
    const active = tasks.filter((task) => !task.completed).length
    const completed = tasks.filter((task) => task.completed).length

    return {
      all,
      active,
      completed,
    }
  }, [tasks])
}
