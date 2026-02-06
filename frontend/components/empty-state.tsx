'use client'

import { CheckCircle2, ListTodo, AlertCircle } from 'lucide-react'
import type { FilterType } from '@/types/task'

interface EmptyStateProps {
  filter: FilterType
}

export function EmptyState({ filter }: EmptyStateProps) {
  const getEmptyStateContent = () => {
    switch (filter) {
      case 'active':
        return {
          icon: CheckCircle2,
          title: 'No active tasks',
          description: 'All caught up! You have no pending tasks.',
        }
      case 'completed':
        return {
          icon: AlertCircle,
          title: 'No completed tasks',
          description: 'Complete some tasks to see them here.',
        }
      case 'all':
      default:
        return {
          icon: ListTodo,
          title: 'No tasks yet',
          description: 'Get started by adding your first task.',
        }
    }
  }

  const { icon: Icon, title, description } = getEmptyStateContent()

  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="rounded-full bg-muted p-4 mb-4">
        <Icon className="h-12 w-12 text-muted-foreground" aria-hidden="true" />
      </div>
      <h3 className="text-lg font-semibold text-foreground mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground max-w-sm">{description}</p>
    </div>
  )
}
