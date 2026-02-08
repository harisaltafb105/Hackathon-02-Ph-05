'use client'

import type { TaskPriority } from '@/types/task'

const PRIORITY_CONFIG: Record<TaskPriority, { label: string; className: string }> = {
  urgent: { label: 'Urgent', className: 'bg-red-100 text-red-800 border-red-200' },
  high: { label: 'High', className: 'bg-orange-100 text-orange-800 border-orange-200' },
  medium: { label: 'Medium', className: 'bg-yellow-100 text-yellow-800 border-yellow-200' },
  low: { label: 'Low', className: 'bg-blue-100 text-blue-800 border-blue-200' },
  none: { label: '', className: '' },
}

interface PriorityBadgeProps {
  priority: TaskPriority
}

export function PriorityBadge({ priority }: PriorityBadgeProps) {
  if (priority === 'none') return null

  const config = PRIORITY_CONFIG[priority]

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${config.className}`}
    >
      {config.label}
    </span>
  )
}
