/**
 * ChatMessages Component for Phase III AI Chatbot
 *
 * Displays chat message history with user/assistant bubbles.
 * Handles tool call display and auto-scroll.
 *
 * Feature: 004-ai-chatbot
 * Date: 2026-01-15
 */

'use client'

import { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Bot, User, CheckCircle2, XCircle, Loader2, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useChatState, useChatActions } from '@/context/chat-context'
import type { ChatMessage, ToolCall } from '@/types/chat'

// Tool call display component
function ToolCallDisplay({ toolCall }: { toolCall: ToolCall }) {
  const getToolDisplayName = (tool: string) => {
    const names: Record<string, string> = {
      add_task: 'Create Task',
      list_tasks: 'List Tasks',
      update_task: 'Update Task',
      complete_task: 'Complete Task',
      delete_task: 'Delete Task',
    }
    return names[tool] || tool
  }

  return (
    <div className="mt-2 rounded-md border bg-muted/50 p-2 text-xs">
      <div className="flex items-center gap-2">
        {toolCall.success ? (
          <CheckCircle2 className="h-3 w-3 text-green-500" />
        ) : (
          <XCircle className="h-3 w-3 text-red-500" />
        )}
        <span className="font-medium">{getToolDisplayName(toolCall.tool)}</span>
      </div>
      {toolCall.result && (
        <div className="mt-1 text-muted-foreground">
          {typeof toolCall.result === 'object' && 'message' in toolCall.result
            ? String(toolCall.result.message)
            : JSON.stringify(toolCall.result, null, 2)}
        </div>
      )}
    </div>
  )
}

// Single message component
function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user'

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
          isUser ? 'bg-primary text-primary-foreground' : 'bg-muted'
        }`}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>

      {/* Message content */}
      <div
        className={`flex max-w-[80%] flex-col ${
          isUser ? 'items-end' : 'items-start'
        }`}
      >
        <div
          className={`rounded-lg px-3 py-2 ${
            isUser
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted text-foreground'
          }`}
        >
          <p className="whitespace-pre-wrap text-sm">{message.content}</p>
        </div>

        {/* Tool calls (only for assistant messages) */}
        {!isUser && message.toolCalls && message.toolCalls.length > 0 && (
          <div className="mt-1 w-full">
            {message.toolCalls.map((tc, idx) => (
              <ToolCallDisplay key={idx} toolCall={tc} />
            ))}
          </div>
        )}

        {/* Timestamp */}
        <span className="mt-1 text-xs text-muted-foreground">
          {message.createdAt.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </span>
      </div>
    </motion.div>
  )
}

// Loading indicator
function LoadingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="flex gap-3"
    >
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted">
        <Bot className="h-4 w-4" />
      </div>
      <div className="flex items-center gap-2 rounded-lg bg-muted px-3 py-2">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span className="text-sm text-muted-foreground">Thinking...</span>
      </div>
    </motion.div>
  )
}

// Empty state
function EmptyState() {
  return (
    <div className="flex h-full flex-col items-center justify-center text-center">
      <Bot className="h-12 w-12 text-muted-foreground" />
      <h3 className="mt-4 text-lg font-medium">AI Task Assistant</h3>
      <p className="mt-2 max-w-xs text-sm text-muted-foreground">
        I can help you manage your tasks. Try saying:
      </p>
      <ul className="mt-3 space-y-1 text-sm text-muted-foreground">
        <li>&quot;Show me my tasks&quot;</li>
        <li>&quot;Add a task to buy groceries&quot;</li>
        <li>&quot;Mark my first task as complete&quot;</li>
      </ul>
    </div>
  )
}

// Main component
export function ChatMessages() {
  const { messages, isLoading, error } = useChatState()
  const { clearError } = useChatActions()
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, isLoading])

  return (
    <div
      ref={scrollRef}
      className="flex-1 overflow-y-auto p-4"
      role="log"
      aria-live="polite"
      aria-label="Chat messages"
    >
      {messages.length === 0 && !isLoading ? (
        <EmptyState />
      ) : (
        <div className="space-y-4">
          <AnimatePresence mode="popLayout">
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            {isLoading && <LoadingIndicator key="loading" />}
          </AnimatePresence>
        </div>
      )}

      {/* Error display */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 flex items-start gap-2 rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive"
        >
          <span className="flex-1">{error}</span>
          <Button
            variant="ghost"
            size="icon-sm"
            className="h-5 w-5 shrink-0 text-destructive hover:bg-destructive/20"
            onClick={clearError}
            aria-label="Dismiss error"
          >
            <X className="h-3 w-3" />
          </Button>
        </motion.div>
      )}
    </div>
  )
}
