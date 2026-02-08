'use client'

import { ArrowUpDown } from 'lucide-react'
import { Button } from '@/components/ui/button'

const SORT_OPTIONS = [
  { value: 'created_at', label: 'Date Created' },
  { value: 'priority', label: 'Priority' },
  { value: 'due_date', label: 'Due Date' },
  { value: 'title', label: 'Title' },
  { value: 'updated_at', label: 'Last Updated' },
] as const

interface SortSelectorProps {
  sortBy: string
  sortOrder: 'asc' | 'desc'
  onSortByChange: (value: string) => void
  onSortOrderToggle: () => void
}

export function SortSelector({ sortBy, sortOrder, onSortByChange, onSortOrderToggle }: SortSelectorProps) {
  return (
    <div className="flex items-center gap-2">
      <select
        value={sortBy}
        onChange={(e) => onSortByChange(e.target.value)}
        className="h-9 rounded-md border border-input bg-background px-3 py-1 text-sm"
        aria-label="Sort by"
      >
        {SORT_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      <Button
        variant="outline"
        size="sm"
        onClick={onSortOrderToggle}
        className="h-9 px-2"
        aria-label={`Sort ${sortOrder === 'asc' ? 'ascending' : 'descending'}`}
      >
        <ArrowUpDown className="h-4 w-4 mr-1" />
        {sortOrder === 'asc' ? 'Asc' : 'Desc'}
      </Button>
    </div>
  )
}
