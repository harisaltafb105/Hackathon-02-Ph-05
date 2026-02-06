'use client'

import { motion } from 'framer-motion'
import { Check, Pencil, Trash2 } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Button } from '@/components/ui/button'
import type { Task } from '@/types/task'

interface TaskCardProps {
  task: Task
  onToggleComplete: (taskId: string) => void
  onEdit: (taskId: string) => void
  onDelete: (taskId: string) => void
}

export function TaskCard({ task, onToggleComplete, onEdit, onDelete }: TaskCardProps) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{
        opacity: task.completed ? 0.6 : 1,
        y: 0,
        scale: task.completed ? 0.95 : 1,
      }}
      exit={{ opacity: 0, x: -100 }}
      transition={{
        duration: 0.2,
        type: 'spring',
        stiffness: 300,
        damping: 20,
      }}
      whileHover={{ scale: task.completed ? 0.96 : 1.01 }}
    >
      <Card
        className={`group relative transition-all ${
          task.completed
            ? 'bg-muted/50 border-muted'
            : 'bg-card hover:shadow-md hover:border-accent/20'
        }`}
      >
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            {/* Checkbox */}
            <div className="pt-0.5">
              <Checkbox
                checked={task.completed}
                onCheckedChange={() => onToggleComplete(task.id)}
                aria-label={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
                className="h-5 w-5"
              />
            </div>

            {/* Task content */}
            <div className="flex-1 min-w-0">
              <h3
                className={`font-medium text-base ${
                  task.completed
                    ? 'line-through text-muted-foreground'
                    : 'text-foreground'
                }`}
              >
                {task.title}
              </h3>
              {task.description && (
                <p
                  className={`mt-1 text-sm ${
                    task.completed
                      ? 'line-through text-muted-foreground/80'
                      : 'text-muted-foreground'
                  }`}
                >
                  {task.description}
                </p>
              )}
              <p className="mt-2 text-xs text-muted-foreground">
                {new Date(task.createdAt).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                })}
              </p>
            </div>

            {/* Action buttons (visible on hover) */}
            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onEdit(task.id)}
                aria-label={`Edit ${task.title}`}
                className="h-8 w-8 p-0"
              >
                <Pencil className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onDelete(task.id)}
                aria-label={`Delete ${task.title}`}
                className="h-8 w-8 p-0 text-destructive hover:text-destructive"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>

            {/* Completion icon */}
            {task.completed && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 200, damping: 15 }}
                className="absolute top-4 right-4 text-muted-foreground"
              >
                <Check className="h-5 w-5" aria-label="Completed" />
              </motion.div>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
