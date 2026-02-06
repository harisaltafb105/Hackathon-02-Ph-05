/**
 * ChatButton Component for Phase III AI Chatbot
 *
 * Floating action button that toggles the chat drawer.
 * Fixed position in bottom-right corner.
 * Only visible when user is authenticated.
 *
 * Feature: 004-ai-chatbot
 * Date: 2026-01-15
 */

'use client'

import { MessageCircle, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/context/auth-context'
import { useChatState, useChatActions } from '@/context/chat-context'

export function ChatButton() {
  const { isAuthenticated } = useAuth()
  const { isOpen } = useChatState()
  const { toggleChat } = useChatActions()

  // Only show when authenticated
  if (!isAuthenticated) {
    return null
  }

  return (
    <motion.div
      className="fixed bottom-6 right-6 z-50"
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: 'spring', stiffness: 260, damping: 20 }}
    >
      <Button
        onClick={toggleChat}
        size="icon-lg"
        className="h-14 w-14 rounded-full shadow-lg hover:shadow-xl transition-shadow"
        aria-label={isOpen ? 'Close chat' : 'Open chat'}
      >
        <AnimatePresence mode="wait" initial={false}>
          {isOpen ? (
            <motion.div
              key="close"
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: 90, opacity: 0 }}
              transition={{ duration: 0.15 }}
            >
              <X className="h-6 w-6" />
            </motion.div>
          ) : (
            <motion.div
              key="chat"
              initial={{ rotate: 90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: -90, opacity: 0 }}
              transition={{ duration: 0.15 }}
            >
              <MessageCircle className="h-6 w-6" />
            </motion.div>
          )}
        </AnimatePresence>
      </Button>
    </motion.div>
  )
}
