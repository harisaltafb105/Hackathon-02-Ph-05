'use client'

import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useTaskCounts } from '@/hooks/use-task-counts'
import { useTasks } from '@/context/task-context'
import { useTaskActions } from '@/context/task-context'
import type { FilterType } from '@/types/task'
import { useMemo, useState } from 'react'
import { AlertCircle, X } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function FilterTabs() {
  const { ui, tasks } = useTasks()
  const dispatch = useTaskActions()
  const counts = useTaskCounts()

  // Advanced filter states
  const [priorityFilter, setPriorityFilter] = useState<string | undefined>()
  const [overdueOnly, setOverdueOnly] = useState(false)

  const handleFilterChange = (value: string) => {
    dispatch({ type: 'SET_FILTER', payload: value as FilterType })
  }

  // Count overdue tasks
  const overdueCount = useMemo(
    () => tasks.filter((t) => t.isOverdue && !t.completed).length,
    [tasks]
  )

  // Unique priorities present in tasks
  const priorities = useMemo(() => {
    const set = new Set(tasks.map((t) => t.priority).filter((p) => p !== 'none'))
    return Array.from(set)
  }, [tasks])

  const hasActiveAdvancedFilter = !!priorityFilter || overdueOnly

  const clearAdvancedFilters = () => {
    setPriorityFilter(undefined)
    setOverdueOnly(false)
  }

  return (
    <div className="space-y-3">
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

      {/* Advanced filter chips */}
      <div className="flex items-center gap-2 flex-wrap">
        {/* Priority filter */}
        {priorities.length > 0 && (
          <div className="flex items-center gap-1">
            {priorities.map((p) => (
              <Button
                key={p}
                variant={priorityFilter === p ? 'default' : 'outline'}
                size="sm"
                className="h-7 text-xs capitalize"
                onClick={() => setPriorityFilter(priorityFilter === p ? undefined : p)}
              >
                {p}
              </Button>
            ))}
          </div>
        )}

        {/* Overdue filter */}
        {overdueCount > 0 && (
          <Button
            variant={overdueOnly ? 'destructive' : 'outline'}
            size="sm"
            className="h-7 text-xs"
            onClick={() => setOverdueOnly(!overdueOnly)}
          >
            <AlertCircle className="h-3 w-3 mr-1" />
            Overdue ({overdueCount})
          </Button>
        )}

        {/* Clear all advanced filters */}
        {hasActiveAdvancedFilter && (
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs"
            onClick={clearAdvancedFilters}
          >
            <X className="h-3 w-3 mr-1" />
            Clear filters
          </Button>
        )}
      </div>
    </div>
  )
}
