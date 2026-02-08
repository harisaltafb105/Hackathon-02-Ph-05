'use client'

import { useState, useCallback } from 'react'
import type { TaskFilters } from '@/types/task'

export function useTaskFilters() {
  const [filters, setFilters] = useState<TaskFilters>({
    sortBy: 'created_at',
    sortOrder: 'desc',
    limit: 50,
    offset: 0,
  })

  const setSearch = useCallback((q: string) => {
    setFilters((prev) => ({ ...prev, q: q || undefined, offset: 0 }))
  }, [])

  const setPriorityFilter = useCallback((priority: string | undefined) => {
    setFilters((prev) => ({ ...prev, priority, offset: 0 }))
  }, [])

  const setTagFilter = useCallback((tag: string | undefined) => {
    setFilters((prev) => ({ ...prev, tag, offset: 0 }))
  }, [])

  const setOverdueFilter = useCallback((overdue: boolean | undefined) => {
    setFilters((prev) => ({ ...prev, overdue, offset: 0 }))
  }, [])

  const setCompletedFilter = useCallback((completed: boolean | undefined) => {
    setFilters((prev) => ({ ...prev, completed, offset: 0 }))
  }, [])

  const setSortBy = useCallback((sortBy: TaskFilters['sortBy']) => {
    setFilters((prev) => ({ ...prev, sortBy, offset: 0 }))
  }, [])

  const toggleSortOrder = useCallback(() => {
    setFilters((prev) => ({
      ...prev,
      sortOrder: prev.sortOrder === 'asc' ? 'desc' : 'asc',
      offset: 0,
    }))
  }, [])

  const setPage = useCallback((offset: number) => {
    setFilters((prev) => ({ ...prev, offset }))
  }, [])

  const clearFilters = useCallback(() => {
    setFilters({
      sortBy: 'created_at',
      sortOrder: 'desc',
      limit: 50,
      offset: 0,
    })
  }, [])

  return {
    filters,
    setSearch,
    setPriorityFilter,
    setTagFilter,
    setOverdueFilter,
    setCompletedFilter,
    setSortBy,
    toggleSortOrder,
    setPage,
    clearFilters,
  }
}
