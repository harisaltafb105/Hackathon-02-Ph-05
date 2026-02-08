'use client'

import { useState, useRef } from 'react'
import { X } from 'lucide-react'
import { Input } from '@/components/ui/input'

interface TagInputProps {
  tags: string[]
  onChange: (tags: string[]) => void
  suggestions?: string[]
  disabled?: boolean
}

export function TagInput({ tags, onChange, suggestions = [], disabled = false }: TagInputProps) {
  const [input, setInput] = useState('')
  const [showSuggestions, setShowSuggestions] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const filteredSuggestions = suggestions.filter(
    (s) => s.toLowerCase().includes(input.toLowerCase()) && !tags.includes(s)
  )

  const addTag = (tag: string) => {
    const normalized = tag.trim().toLowerCase().replace(/[^a-z0-9_-]/g, '')
    if (normalized && !tags.includes(normalized) && tags.length < 20) {
      onChange([...tags, normalized])
    }
    setInput('')
    setShowSuggestions(false)
    inputRef.current?.focus()
  }

  const removeTag = (tag: string) => {
    onChange(tags.filter((t) => t !== tag))
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      if (input.trim()) addTag(input)
    }
    if (e.key === 'Backspace' && !input && tags.length > 0) {
      removeTag(tags[tags.length - 1])
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-1.5 min-h-[32px]">
        {tags.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-accent text-accent-foreground text-xs font-medium"
          >
            {tag}
            {!disabled && (
              <button
                type="button"
                onClick={() => removeTag(tag)}
                className="hover:text-destructive"
                aria-label={`Remove tag ${tag}`}
              >
                <X className="h-3 w-3" />
              </button>
            )}
          </span>
        ))}
      </div>
      <div className="relative">
        <Input
          ref={inputRef}
          value={input}
          onChange={(e) => {
            setInput(e.target.value)
            setShowSuggestions(true)
          }}
          onKeyDown={handleKeyDown}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          placeholder={tags.length >= 20 ? 'Max tags reached' : 'Add tag...'}
          disabled={disabled || tags.length >= 20}
          className="text-sm"
        />
        {showSuggestions && input && filteredSuggestions.length > 0 && (
          <div className="absolute z-10 mt-1 w-full bg-popover border rounded-md shadow-md max-h-32 overflow-y-auto">
            {filteredSuggestions.slice(0, 5).map((s) => (
              <button
                key={s}
                type="button"
                onMouseDown={(e) => {
                  e.preventDefault()
                  addTag(s)
                }}
                className="w-full text-left px-3 py-1.5 text-sm hover:bg-accent"
              >
                {s}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
