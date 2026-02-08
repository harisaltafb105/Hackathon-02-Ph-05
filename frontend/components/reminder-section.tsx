'use client'

import { useState, useEffect, useCallback } from 'react'
import { Bell, Trash2, Plus, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { apiClient } from '@/lib/api-client'
import type { Reminder } from '@/types/task'

interface ReminderSectionProps {
  taskId: string
  userId: string
  hasDueDate: boolean
}

export function ReminderSection({ taskId, userId, hasDueDate }: ReminderSectionProps) {
  const [reminders, setReminders] = useState<Reminder[]>([])
  const [loading, setLoading] = useState(false)
  const [adding, setAdding] = useState(false)
  const [showAddForm, setShowAddForm] = useState(false)
  const [triggerAt, setTriggerAt] = useState('')
  const [relativeMode, setRelativeMode] = useState<'absolute' | 'relative'>('absolute')
  const [relativeToDue, setRelativeToDue] = useState('-1d')

  const fetchReminders = useCallback(async () => {
    setLoading(true)
    const result = await apiClient.getReminders(userId, taskId)
    if (result.success && result.data) {
      setReminders(result.data.filter((r) => r.status === 'pending'))
    }
    setLoading(false)
  }, [userId, taskId])

  useEffect(() => {
    fetchReminders()
  }, [fetchReminders])

  const handleAdd = async () => {
    setAdding(true)
    const payload: { triggerAt?: string; relativeToDue?: string } = {}
    if (relativeMode === 'absolute' && triggerAt) {
      payload.triggerAt = new Date(triggerAt).toISOString()
    } else if (relativeMode === 'relative' && relativeToDue) {
      payload.relativeToDue = relativeToDue
    }

    const result = await apiClient.createReminder(userId, taskId, payload)
    if (result.success) {
      await fetchReminders()
      setShowAddForm(false)
      setTriggerAt('')
    }
    setAdding(false)
  }

  const handleDelete = async (reminderId: string) => {
    await apiClient.deleteReminder(userId, taskId, reminderId)
    setReminders((prev) => prev.filter((r) => r.id !== reminderId))
  }

  return (
    <div className="space-y-3 border-t pt-3 mt-3">
      <div className="flex items-center justify-between">
        <Label className="flex items-center gap-1.5 text-sm font-medium">
          <Bell className="h-3.5 w-3.5" />
          Reminders
        </Label>
        {!showAddForm && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="h-7 text-xs"
            onClick={() => setShowAddForm(true)}
          >
            <Plus className="h-3 w-3 mr-1" />
            Add
          </Button>
        )}
      </div>

      {/* Existing reminders */}
      {loading ? (
        <p className="text-xs text-muted-foreground">Loading reminders...</p>
      ) : reminders.length === 0 ? (
        <p className="text-xs text-muted-foreground">No active reminders</p>
      ) : (
        <div className="space-y-1.5">
          {reminders.map((r) => (
            <div
              key={r.id}
              className="flex items-center justify-between px-2 py-1.5 bg-muted/50 rounded text-xs"
            >
              <span>
                {new Date(r.triggerAt).toLocaleString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                  hour: 'numeric',
                  minute: '2-digit',
                })}
              </span>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 text-destructive hover:text-destructive"
                onClick={() => handleDelete(r.id)}
              >
                <Trash2 className="h-3 w-3" />
              </Button>
            </div>
          ))}
        </div>
      )}

      {/* Add reminder form */}
      {showAddForm && (
        <div className="space-y-2 p-2 border rounded-md bg-muted/30">
          {hasDueDate && (
            <div className="flex gap-2">
              <Button
                type="button"
                variant={relativeMode === 'absolute' ? 'default' : 'outline'}
                size="sm"
                className="h-7 text-xs"
                onClick={() => setRelativeMode('absolute')}
              >
                Date/Time
              </Button>
              <Button
                type="button"
                variant={relativeMode === 'relative' ? 'default' : 'outline'}
                size="sm"
                className="h-7 text-xs"
                onClick={() => setRelativeMode('relative')}
              >
                Before Due
              </Button>
            </div>
          )}

          {relativeMode === 'absolute' ? (
            <Input
              type="datetime-local"
              value={triggerAt}
              onChange={(e) => setTriggerAt(e.target.value)}
              className="text-sm"
            />
          ) : (
            <select
              value={relativeToDue}
              onChange={(e) => setRelativeToDue(e.target.value)}
              className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
            >
              <option value="-15m">15 minutes before</option>
              <option value="-1h">1 hour before</option>
              <option value="-1d">1 day before</option>
              <option value="-2d">2 days before</option>
              <option value="-7d">1 week before</option>
            </select>
          )}

          <div className="flex gap-2">
            <Button
              type="button"
              size="sm"
              className="h-7 text-xs"
              onClick={handleAdd}
              disabled={adding || (relativeMode === 'absolute' && !triggerAt)}
            >
              {adding ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : null}
              Save
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="h-7 text-xs"
              onClick={() => setShowAddForm(false)}
            >
              Cancel
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
