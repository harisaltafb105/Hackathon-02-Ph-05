'use client'

import { X } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

interface DatePickerProps {
  value: string | null
  onChange: (value: string | null) => void
  disabled?: boolean
}

export function DatePicker({ value, onChange, disabled = false }: DatePickerProps) {
  return (
    <div className="flex items-center gap-2">
      <Input
        type="date"
        value={value || ''}
        onChange={(e) => onChange(e.target.value || null)}
        disabled={disabled}
        className="text-sm"
      />
      {value && (
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => onChange(null)}
          disabled={disabled}
          className="h-8 w-8 p-0"
          aria-label="Clear date"
        >
          <X className="h-4 w-4" />
        </Button>
      )}
    </div>
  )
}
