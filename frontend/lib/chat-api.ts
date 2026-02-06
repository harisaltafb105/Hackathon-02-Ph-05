/**
 * Chat API Client for Phase III AI Chatbot
 *
 * Provides API methods for chat functionality.
 * Communicates with FastAPI backend chat endpoints.
 *
 * Feature: 004-ai-chatbot
 * Date: 2026-01-15
 */

import type { ChatResponse, ChatMessage, ConversationSummary, Conversation, ToolCall } from '@/types/chat'
import type { APIResponse } from '@/types/auth'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * Get auth token from localStorage
 */
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null
  const authData = localStorage.getItem('auth-state')
  if (!authData) return null
  try {
    const parsed = JSON.parse(authData)
    return parsed.token || null
  } catch {
    return null
  }
}

/**
 * Get user ID from localStorage
 */
function getUserId(): string | null {
  if (typeof window === 'undefined') return null
  const authData = localStorage.getItem('auth-state')
  if (!authData) return null
  try {
    const parsed = JSON.parse(authData)
    return parsed.user?.id || null
  } catch {
    return null
  }
}

/**
 * Send a chat message
 */
export async function sendMessage(
  message: string,
  conversationId?: string | null
): Promise<APIResponse<ChatResponse>> {
  const token = getAuthToken()
  const userId = getUserId()

  if (!token || !userId) {
    return {
      success: false,
      data: null,
      error: 'Not authenticated',
      statusCode: 401,
    }
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId || null,
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      return {
        success: false,
        data: null,
        error: data.detail || data.error || 'Failed to send message',
        statusCode: response.status,
      }
    }

    // Transform backend response to frontend format
    return {
      success: true,
      data: {
        conversationId: data.conversation_id,
        response: data.response,
        toolCalls: (data.tool_calls || []).map((tc: Record<string, unknown>) => ({
          tool: tc.tool,
          parameters: tc.parameters,
          result: tc.result,
          success: tc.success,
        })),
      },
      error: null,
      statusCode: response.status,
    }
  } catch (error) {
    return {
      success: false,
      data: null,
      error: 'Network error - could not connect to server',
      statusCode: 500,
    }
  }
}

/**
 * Get list of conversations
 */
export async function getConversations(
  limit: number = 20,
  offset: number = 0
): Promise<APIResponse<{ conversations: ConversationSummary[]; total: number }>> {
  const token = getAuthToken()
  const userId = getUserId()

  if (!token || !userId) {
    return {
      success: false,
      data: null,
      error: 'Not authenticated',
      statusCode: 401,
    }
  }

  try {
    const params = new URLSearchParams({
      limit: String(limit),
      offset: String(offset),
    })

    const response = await fetch(
      `${API_BASE_URL}/api/${userId}/conversations?${params}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    )

    const data = await response.json()

    if (!response.ok) {
      return {
        success: false,
        data: null,
        error: data.detail || data.error || 'Failed to load conversations',
        statusCode: response.status,
      }
    }

    return {
      success: true,
      data: {
        conversations: (data.conversations || []).map((conv: Record<string, unknown>) => ({
          id: conv.id,
          title: conv.title,
          createdAt: new Date(conv.created_at as string),
          updatedAt: new Date(conv.updated_at as string),
          messageCount: conv.message_count,
        })),
        total: data.total,
      },
      error: null,
      statusCode: response.status,
    }
  } catch (error) {
    return {
      success: false,
      data: null,
      error: 'Network error - could not connect to server',
      statusCode: 500,
    }
  }
}

/**
 * Get conversation history
 */
export async function getConversationHistory(
  conversationId: string,
  limit: number = 50
): Promise<APIResponse<Conversation>> {
  const token = getAuthToken()
  const userId = getUserId()

  if (!token || !userId) {
    return {
      success: false,
      data: null,
      error: 'Not authenticated',
      statusCode: 401,
    }
  }

  try {
    const params = new URLSearchParams({
      limit: String(limit),
    })

    const response = await fetch(
      `${API_BASE_URL}/api/${userId}/conversations/${conversationId}?${params}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    )

    const data = await response.json()

    if (!response.ok) {
      return {
        success: false,
        data: null,
        error: data.detail || data.error || 'Failed to load conversation',
        statusCode: response.status,
      }
    }

    return {
      success: true,
      data: {
        id: data.id,
        title: data.title,
        createdAt: new Date(data.created_at),
        updatedAt: new Date(data.updated_at),
        messages: (data.messages || []).map((msg: Record<string, unknown>) => ({
          id: msg.id,
          role: msg.role,
          content: msg.content,
          createdAt: new Date(msg.created_at as string),
          toolCalls: (msg.tool_calls as Record<string, unknown>[] || []).map((tc) => ({
            tool: tc.tool,
            parameters: tc.parameters,
            result: tc.result,
            success: tc.success,
          })),
        })),
        hasMore: data.has_more || false,
      },
      error: null,
      statusCode: response.status,
    }
  } catch (error) {
    return {
      success: false,
      data: null,
      error: 'Network error - could not connect to server',
      statusCode: 500,
    }
  }
}

/**
 * Delete a conversation
 */
export async function deleteConversation(
  conversationId: string
): Promise<APIResponse<void>> {
  const token = getAuthToken()
  const userId = getUserId()

  if (!token || !userId) {
    return {
      success: false,
      data: null,
      error: 'Not authenticated',
      statusCode: 401,
    }
  }

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/${userId}/conversations/${conversationId}`,
      {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    )

    if (response.status === 204) {
      return {
        success: true,
        data: null,
        error: null,
        statusCode: 204,
      }
    }

    const data = await response.json()

    return {
      success: false,
      data: null,
      error: data.detail || data.error || 'Failed to delete conversation',
      statusCode: response.status,
    }
  } catch (error) {
    return {
      success: false,
      data: null,
      error: 'Network error - could not connect to server',
      statusCode: 500,
    }
  }
}
