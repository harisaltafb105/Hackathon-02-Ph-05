'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import type { TaskFormData } from '@/types/task'
import { useEffect, useRef } from 'react'

// Zod validation schema
const taskSchema = z.object({
  title: z
    .string()
    .min(1, 'Title is required')
    .max(200, 'Title must be 200 characters or less')
    .trim(),
  description: z
    .string()
    .max(1000, 'Description must be 1000 characters or less')
    .optional()
    .default(''),
})

interface TaskFormProps {
  mode: 'add' | 'edit'
  initialData?: Partial<TaskFormData>
  onSubmit: (data: TaskFormData) => void | Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

export function TaskForm({
  mode,
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
}: TaskFormProps) {
  const titleInputRef = useRef<HTMLInputElement>(null)

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: initialData?.title || '',
      description: initialData?.description || '',
    },
  })

  // Auto-focus title input when form mounts
  useEffect(() => {
    titleInputRef.current?.focus()
  }, [])

  // Watch description for character count
  const description = watch('description')
  const descriptionLength = description?.length || 0
  const descriptionRemaining = 1000 - descriptionLength

  const handleFormSubmit = async (data: TaskFormData) => {
    await onSubmit(data)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      e.preventDefault()
      onCancel()
    }
  }

  return (
    <form
      onSubmit={handleSubmit(handleFormSubmit)}
      onKeyDown={handleKeyDown}
      className="space-y-4"
    >
      {/* Title field */}
      <div className="space-y-2">
        <Label htmlFor="title">
          Title <span className="text-destructive">*</span>
        </Label>
        <Input
          id="title"
          {...register('title')}
          ref={(e) => {
            register('title').ref(e)
            if (e) titleInputRef.current = e
          }}
          placeholder="Enter task title..."
          disabled={isLoading}
          aria-invalid={!!errors.title}
          aria-describedby={errors.title ? 'title-error' : undefined}
          className={errors.title ? 'border-destructive' : ''}
        />
        {errors.title && (
          <p id="title-error" className="text-sm text-destructive" role="alert">
            {errors.title.message}
          </p>
        )}
      </div>

      {/* Description field */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label htmlFor="description">Description</Label>
          <span
            className={`text-xs ${
              descriptionRemaining < 100
                ? 'text-destructive font-medium'
                : 'text-muted-foreground'
            }`}
            aria-live="polite"
          >
            {descriptionRemaining} characters remaining
          </span>
        </div>
        <textarea
          id="description"
          {...register('description')}
          placeholder="Add details about your task..."
          disabled={isLoading}
          rows={4}
          aria-invalid={!!errors.description}
          aria-describedby={errors.description ? 'description-error' : undefined}
          className={`flex min-h-[80px] w-full rounded-md border bg-background px-3 py-2 text-base ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm ${
            errors.description ? 'border-destructive' : 'border-input'
          }`}
        />
        {errors.description && (
          <p id="description-error" className="text-sm text-destructive" role="alert">
            {errors.description.message}
          </p>
        )}
      </div>

      {/* Action buttons */}
      <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-2 pt-2">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isLoading}
          className="w-full sm:w-auto"
        >
          Cancel
        </Button>
        <Button
          type="submit"
          disabled={isLoading}
          className="w-full sm:w-auto"
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              {mode === 'add' ? 'Adding...' : 'Updating...'}
            </>
          ) : (
            <>{mode === 'add' ? 'Add Task' : 'Update Task'}</>
          )}
        </Button>
      </div>
    </form>
  )
}
