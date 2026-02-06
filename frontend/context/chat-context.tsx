/**
 * Chat Context for Phase III AI Chatbot
 *
 * Provides chat state and actions throughout the application.
 * Follows the same pattern as auth-context.tsx and task-context.tsx.
 *
 * Feature: 004-ai-chatbot
 * Date: 2026-01-15
 */

'use client'

import {
  createContext,
  useContext,
  useReducer,
  useCallback,
  useEffect,
  type ReactNode,
} from 'react'
import type { ChatState, ChatAction, ChatMessage } from '@/types/chat'
import {
  sendMessage as apiSendMessage,
  getConversationHistory,
} from '@/lib/chat-api'
import { useAuth } from '@/context/auth-context'

// LocalStorage key
const CHAT_STORAGE_KEY = 'chat_conversation'

// LocalStorage helpers
function getStoredConversationId(): string | null {
  if (typeof window === 'undefined') return null
  try {
    return localStorage.getItem(CHAT_STORAGE_KEY)
  } catch {
    return null
  }
}

function setStoredConversationId(id: string | null): void {
  if (typeof window === 'undefined') return
  try {
    if (id) {
      localStorage.setItem(CHAT_STORAGE_KEY, id)
    } else {
      localStorage.removeItem(CHAT_STORAGE_KEY)
    }
  } catch {
    // Ignore storage errors
  }
}

// Initial state
const initialState: ChatState = {
  isOpen: false,
  isLoading: false,
  conversationId: null,
  messages: [],
  error: null,
}

// Reducer function
function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case 'OPEN_CHAT':
      return {
        ...state,
        isOpen: true,
      }

    case 'CLOSE_CHAT':
      return {
        ...state,
        isOpen: false,
      }

    case 'TOGGLE_CHAT':
      return {
        ...state,
        isOpen: !state.isOpen,
      }

    case 'SEND_MESSAGE_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      }

    case 'SEND_MESSAGE_SUCCESS':
      return {
        ...state,
        isLoading: false,
        conversationId: action.payload.conversationId,
        messages: [
          ...state.messages,
          action.payload.userMessage,
          action.payload.assistantMessage,
        ],
        error: null,
      }

    case 'SEND_MESSAGE_FAILURE':
      return {
        ...state,
        isLoading: false,
        error: action.payload.error,
      }

    case 'LOAD_HISTORY_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      }

    case 'LOAD_HISTORY_SUCCESS':
      return {
        ...state,
        isLoading: false,
        conversationId: action.payload.conversationId,
        messages: action.payload.messages,
        error: null,
      }

    case 'LOAD_HISTORY_FAILURE':
      return {
        ...state,
        isLoading: false,
        error: action.payload.error,
      }

    case 'CLEAR_CONVERSATION':
      return {
        ...state,
        conversationId: null,
        messages: [],
        error: null,
      }

    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      }

    default:
      return state
  }
}

// Context types
interface ChatActions {
  openChat: () => void
  closeChat: () => void
  toggleChat: () => void
  sendMessage: (message: string) => Promise<void>
  loadHistory: (conversationId: string) => Promise<void>
  clearConversation: () => void
  clearError: () => void
}

// Context creation
const ChatStateContext = createContext<ChatState | undefined>(undefined)
const ChatActionsContext = createContext<ChatActions | undefined>(undefined)

// Provider component
export function ChatProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(chatReducer, initialState)
  const { isAuthenticated } = useAuth()

  // Persist conversation ID to localStorage when it changes
  useEffect(() => {
    setStoredConversationId(state.conversationId)
  }, [state.conversationId])

  // Restore conversation from localStorage on mount
  useEffect(() => {
    if (!isAuthenticated) return

    const storedId = getStoredConversationId()
    if (storedId && !state.conversationId && state.messages.length === 0) {
      // Load history for stored conversation
      const loadStoredHistory = async () => {
        dispatch({ type: 'LOAD_HISTORY_START' })
        const result = await getConversationHistory(storedId)
        if (result.success && result.data) {
          dispatch({
            type: 'LOAD_HISTORY_SUCCESS',
            payload: {
              conversationId: storedId,
              messages: result.data.messages,
              hasMore: result.data.hasMore,
            },
          })
        } else {
          // Stored conversation no longer exists, clear storage
          setStoredConversationId(null)
          dispatch({ type: 'LOAD_HISTORY_FAILURE', payload: { error: '' } })
        }
      }
      loadStoredHistory()
    }
  }, [isAuthenticated]) // eslint-disable-line react-hooks/exhaustive-deps

  // Clear chat state when user logs out
  useEffect(() => {
    if (!isAuthenticated) {
      dispatch({ type: 'CLEAR_CONVERSATION' })
      setStoredConversationId(null)
    }
  }, [isAuthenticated])

  // Actions
  const openChat = useCallback(() => {
    dispatch({ type: 'OPEN_CHAT' })
  }, [])

  const closeChat = useCallback(() => {
    dispatch({ type: 'CLOSE_CHAT' })
  }, [])

  const toggleChat = useCallback(() => {
    dispatch({ type: 'TOGGLE_CHAT' })
  }, [])

  const sendMessage = useCallback(
    async (message: string) => {
      if (!isAuthenticated) {
        dispatch({
          type: 'SEND_MESSAGE_FAILURE',
          payload: { error: 'Please log in to use the chat' },
        })
        return
      }

      dispatch({ type: 'SEND_MESSAGE_START' })

      const result = await apiSendMessage(message, state.conversationId)

      if (result.success && result.data) {
        const userMessage: ChatMessage = {
          id: `user-${Date.now()}`,
          role: 'user',
          content: message,
          createdAt: new Date(),
        }

        const assistantMessage: ChatMessage = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: result.data.response,
          createdAt: new Date(),
          toolCalls: result.data.toolCalls,
        }

        dispatch({
          type: 'SEND_MESSAGE_SUCCESS',
          payload: {
            conversationId: result.data.conversationId,
            userMessage,
            assistantMessage,
          },
        })

        // Notify task context to refresh if any task-modifying tool calls succeeded
        const taskModifyingTools = ['add_task', 'update_task', 'delete_task', 'complete_task']
        const hasTaskModification = result.data.toolCalls?.some(
          (tc) => taskModifyingTools.includes(tc.tool) && tc.success
        )
        if (hasTaskModification) {
          window.dispatchEvent(new CustomEvent('tasks-modified-by-chat'))
        }
      } else {
        dispatch({
          type: 'SEND_MESSAGE_FAILURE',
          payload: { error: result.error || 'Failed to send message' },
        })
      }
    },
    [isAuthenticated, state.conversationId]
  )

  const loadHistory = useCallback(
    async (conversationId: string) => {
      if (!isAuthenticated) {
        return
      }

      dispatch({ type: 'LOAD_HISTORY_START' })

      const result = await getConversationHistory(conversationId)

      if (result.success && result.data) {
        dispatch({
          type: 'LOAD_HISTORY_SUCCESS',
          payload: {
            conversationId,
            messages: result.data.messages,
            hasMore: result.data.hasMore,
          },
        })
      } else {
        dispatch({
          type: 'LOAD_HISTORY_FAILURE',
          payload: { error: result.error || 'Failed to load history' },
        })
      }
    },
    [isAuthenticated]
  )

  const clearConversation = useCallback(() => {
    dispatch({ type: 'CLEAR_CONVERSATION' })
  }, [])

  const clearError = useCallback(() => {
    dispatch({ type: 'CLEAR_ERROR' })
  }, [])

  const actions: ChatActions = {
    openChat,
    closeChat,
    toggleChat,
    sendMessage,
    loadHistory,
    clearConversation,
    clearError,
  }

  return (
    <ChatStateContext.Provider value={state}>
      <ChatActionsContext.Provider value={actions}>
        {children}
      </ChatActionsContext.Provider>
    </ChatStateContext.Provider>
  )
}

// Hooks
export function useChatState(): ChatState {
  const context = useContext(ChatStateContext)
  if (context === undefined) {
    throw new Error('useChatState must be used within ChatProvider')
  }
  return context
}

export function useChatActions(): ChatActions {
  const context = useContext(ChatActionsContext)
  if (context === undefined) {
    throw new Error('useChatActions must be used within ChatProvider')
  }
  return context
}

// Combined hook for convenience
export function useChat() {
  return {
    ...useChatState(),
    ...useChatActions(),
  }
}
