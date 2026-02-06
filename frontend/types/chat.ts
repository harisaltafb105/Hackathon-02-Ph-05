/**
 * Chat Types for Phase III AI Chatbot
 *
 * Defines TypeScript types for chat functionality.
 * Matches backend schemas from specs/004-ai-chatbot/contracts/chat-api.yaml
 *
 * Feature: 004-ai-chatbot
 * Date: 2026-01-15
 */

/**
 * Tool call response from AI assistant
 */
export interface ToolCall {
  tool: string
  parameters: Record<string, unknown>
  result: Record<string, unknown> | null
  success: boolean
}

/**
 * Chat message
 */
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  createdAt: Date
  toolCalls?: ToolCall[]
}

/**
 * Conversation summary for listing
 */
export interface ConversationSummary {
  id: string
  title: string | null
  createdAt: Date
  updatedAt: Date
  messageCount: number
}

/**
 * Full conversation with messages
 */
export interface Conversation {
  id: string
  title: string | null
  createdAt: Date
  updatedAt: Date
  messages: ChatMessage[]
  hasMore: boolean
}

/**
 * Chat request to send a message
 */
export interface ChatRequest {
  message: string
  conversationId?: string | null
}

/**
 * Chat response from backend
 */
export interface ChatResponse {
  conversationId: string
  response: string
  toolCalls: ToolCall[]
}

/**
 * Chat state for context/reducer
 */
export interface ChatState {
  isOpen: boolean
  isLoading: boolean
  conversationId: string | null
  messages: ChatMessage[]
  error: string | null
}

/**
 * Chat action types
 */
export type ChatAction =
  | { type: 'OPEN_CHAT' }
  | { type: 'CLOSE_CHAT' }
  | { type: 'TOGGLE_CHAT' }
  | { type: 'SEND_MESSAGE_START' }
  | { type: 'SEND_MESSAGE_SUCCESS'; payload: { conversationId: string; userMessage: ChatMessage; assistantMessage: ChatMessage } }
  | { type: 'SEND_MESSAGE_FAILURE'; payload: { error: string } }
  | { type: 'LOAD_HISTORY_START' }
  | { type: 'LOAD_HISTORY_SUCCESS'; payload: { conversationId: string; messages: ChatMessage[]; hasMore: boolean } }
  | { type: 'LOAD_HISTORY_FAILURE'; payload: { error: string } }
  | { type: 'CLEAR_CONVERSATION' }
  | { type: 'CLEAR_ERROR' }
