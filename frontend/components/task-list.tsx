'use client'

import { AnimatePresence, motion } from 'framer-motion'
import { TaskCard } from '@/components/task-card'
import { EmptyState } from '@/components/empty-state'
import { SearchBar } from '@/components/search-bar'
import { SortSelector } from '@/components/sort-selector'
import { useFilteredTasks } from '@/hooks/use-filtered-tasks'
import { useTasks, useTaskActions, useTaskAPI } from '@/context/task-context'
import { useState } from 'react'

export function TaskList() {
  const filteredTasks = useFilteredTasks()
  const { ui } = useTasks()
  const dispatch = useTaskActions()
  const { toggleComplete } = useTaskAPI()

  // Local search & sort state (client-side for responsiveness)
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState('created_at')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  const handleToggleComplete = (taskId: string) => {
    toggleComplete(taskId)
  }

  const handleEdit = (taskId: string) => {
    dispatch({ type: 'OPEN_MODAL', payload: { mode: 'edit', taskId } })
  }

  const handleDelete = (taskId: string) => {
    dispatch({ type: 'OPEN_MODAL', payload: { mode: 'delete', taskId } })
  }

  // Apply client-side search
  let displayTasks = filteredTasks
  if (searchQuery) {
    const q = searchQuery.toLowerCase()
    displayTasks = displayTasks.filter(
      (t) =>
        t.title.toLowerCase().includes(q) ||
        (t.description && t.description.toLowerCase().includes(q)) ||
        (t.tags && t.tags.some((tag) => tag.toLowerCase().includes(q)))
    )
  }

  // Apply client-side sort
  const PRIORITY_ORDER: Record<string, number> = { urgent: 4, high: 3, medium: 2, low: 1, none: 0 }
  displayTasks = [...displayTasks].sort((a, b) => {
    let cmp = 0
    switch (sortBy) {
      case 'priority':
        cmp = (PRIORITY_ORDER[a.priority] || 0) - (PRIORITY_ORDER[b.priority] || 0)
        break
      case 'due_date': {
        const aDate = a.dueDate ? new Date(a.dueDate).getTime() : Infinity
        const bDate = b.dueDate ? new Date(b.dueDate).getTime() : Infinity
        cmp = aDate - bDate
        break
      }
      case 'title':
        cmp = a.title.localeCompare(b.title)
        break
      case 'updated_at': {
        const aUp = a.updatedAt ? new Date(a.updatedAt).getTime() : 0
        const bUp = b.updatedAt ? new Date(b.updatedAt).getTime() : 0
        cmp = aUp - bUp
        break
      }
      case 'created_at':
      default: {
        cmp = new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
        break
      }
    }
    return sortOrder === 'asc' ? cmp : -cmp
  })

  return (
    <div className="space-y-4">
      {/* Search & Sort toolbar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex-1">
          <SearchBar value={searchQuery} onChange={setSearchQuery} />
        </div>
        <SortSelector
          sortBy={sortBy}
          sortOrder={sortOrder}
          onSortByChange={setSortBy}
          onSortOrderToggle={() => setSortOrder((o) => (o === 'asc' ? 'desc' : 'asc'))}
        />
      </div>

      {/* Task list */}
      {displayTasks.length === 0 ? (
        searchQuery ? (
          <p className="text-center text-muted-foreground py-8 text-sm">
            No tasks match &quot;{searchQuery}&quot;
          </p>
        ) : (
          <EmptyState filter={ui.activeFilter} />
        )
      ) : (
        <motion.div
          layout
          className="space-y-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          <AnimatePresence mode="popLayout">
            {displayTasks.map((task) => (
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
      )}
    </div>
  )
}
