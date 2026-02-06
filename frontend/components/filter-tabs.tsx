'use client'

import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useTaskCounts } from '@/hooks/use-task-counts'
import { useTasks } from '@/context/task-context'
import { useTaskActions } from '@/context/task-context'
import type { FilterType } from '@/types/task'

export function FilterTabs() {
  const { ui } = useTasks()
  const dispatch = useTaskActions()
  const counts = useTaskCounts()

  const handleFilterChange = (value: string) => {
    dispatch({ type: 'SET_FILTER', payload: value as FilterType })
  }

  return (
    <Tabs value={ui.activeFilter} onValueChange={handleFilterChange} className="w-full">
      <TabsList className="grid w-full grid-cols-3 max-w-md mx-auto">
        <TabsTrigger value="all" className="text-sm">
          All ({counts.all})
        </TabsTrigger>
        <TabsTrigger value="active" className="text-sm">
          Active ({counts.active})
        </TabsTrigger>
        <TabsTrigger value="completed" className="text-sm">
          Completed ({counts.completed})
        </TabsTrigger>
      </TabsList>
    </Tabs>
  )
}
