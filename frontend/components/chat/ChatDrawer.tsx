/**
 * ChatDrawer Component for Phase III AI Chatbot
 *
 * Slide-out chat panel with messages and input.
 * Uses framer-motion for smooth animations.
 *
 * Feature: 004-ai-chatbot
 * Date: 2026-01-15
 */

'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { X, MessageCircle, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useChatState, useChatActions } from '@/context/chat-context'
import { ChatMessages } from './ChatMessages'
import { ChatInput } from './ChatInput'

export function ChatDrawer() {
  const { isOpen, conversationId, messages } = useChatState()
  const { closeChat, clearConversation } = useChatActions()

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-40 bg-black/20 backdrop-blur-sm"
            onClick={closeChat}
            aria-hidden="true"
          />

          {/* Drawer panel */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="fixed bottom-0 right-0 top-0 z-50 flex w-full max-w-md flex-col border-l bg-background shadow-xl sm:w-96"
            role="dialog"
            aria-modal="true"
            aria-label="Chat assistant"
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b px-4 py-3">
              <div className="flex items-center gap-2">
                <MessageCircle className="h-5 w-5 text-primary" />
                <h2 className="font-semibold">Task Assistant</h2>
              </div>
              <div className="flex items-center gap-1">
                {messages.length > 0 && (
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    onClick={clearConversation}
                    aria-label="Start new conversation"
                    title="Start new conversation"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
                <Button
                  variant="ghost"
                  size="icon-sm"
                  onClick={closeChat}
                  aria-label="Close chat"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Messages area */}
            <ChatMessages />

            {/* Input area */}
            <ChatInput />
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
