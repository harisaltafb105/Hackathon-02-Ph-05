# Research: Phase III AI Chatbot Integration

**Feature**: 004-ai-chatbot
**Date**: 2026-01-14
**Phase**: Phase 0 - Research

## Overview

This document consolidates research findings for integrating an AI-powered chatbot into the existing Phase II Todo application using OpenAI Agents SDK, MCP SDK, and OpenAI ChatKit.

---

## 1. Phase II Architecture Validation

### Decision: Existing Backend Integration Points Confirmed

**Rationale**: Phase II backend provides all required CRUD operations and authentication mechanisms.

**Verified Components**:

| Component | Location | Status |
|-----------|----------|--------|
| Task Model | `backend/models.py:63-131` | UUID-based, user_id scoped |
| JWT Auth | `backend/auth.py:19-76` | Better Auth HS256 verification |
| User Isolation | `backend/auth.py:79-104` | Path param vs JWT validation |
| Task Endpoints | `backend/routers/tasks.py` | Full CRUD at `/api/{user_id}/tasks` |
| Database | Neon PostgreSQL | SQLModel ORM with async engine |

**Alternatives Considered**:
- Creating separate chatbot microservice → Rejected (violates monorepo principle, duplicates auth logic)
- Direct database access from AI agent → Rejected (violates Constitution VIII)

---

## 2. OpenAI Agents SDK Integration Pattern

### Decision: Stateless Agent per Request with MCP Tool Binding

**Rationale**: OpenAI Agents SDK supports tool-calling through function definitions. Agents are instantiated per request with conversation history passed in.

**Integration Architecture**:
```
User Message → FastAPI → Load History from DB → Instantiate Agent → Execute with MCP Tools → Persist Response → Return to User
```

**Key Design Choices**:

1. **Agent Lifecycle**: Stateless - agent created per request, no persistent agent instance
2. **Conversation Context**: Loaded from database before each request, passed to agent
3. **Tool Access**: MCP tools registered at agent creation time
4. **Response Streaming**: Not in MVP scope (batch response mode)

**Alternatives Considered**:
- Persistent agent instance in memory → Rejected (violates Constitution IX - stateless server)
- Streaming responses via WebSocket → Deferred (adds complexity, not required for MVP)

---

## 3. MCP SDK Tool Implementation

### Decision: Internal Python MCP Server with FastAPI Integration

**Rationale**: MCP SDK provides standardized tool interface that OpenAI Agents SDK can consume. Tools wrap existing backend CRUD logic.

**Tool Registry**:

| Tool Name | Operation | FastAPI Endpoint Equivalent |
|-----------|-----------|---------------------------|
| `add_task` | Create task | POST `/api/{user_id}/tasks` |
| `list_tasks` | Read all tasks | GET `/api/{user_id}/tasks` |
| `update_task` | Update task | PATCH `/api/{user_id}/tasks/{id}` |
| `delete_task` | Delete task | DELETE `/api/{user_id}/tasks/{id}` |
| `complete_task` | Toggle complete | PATCH with `completed: true` |

**User Isolation Strategy**:
- Each tool receives `user_id` from authenticated backend context
- Tools query database directly (not via HTTP) for performance
- Same SQLModel queries as existing endpoints

**Alternatives Considered**:
- HTTP calls to own endpoints → Rejected (unnecessary network overhead, latency)
- Separate MCP process → Rejected (adds operational complexity, harder to share DB session)

---

## 4. Chat Endpoint Design

### Decision: Single Endpoint with Conversation Context

**Rationale**: RESTful endpoint pattern consistent with Phase II. Conversation ID enables history restoration.

**Endpoint Contract**:
```
POST /api/{user_id}/chat
Authorization: Bearer <jwt_token>

Request:
{
  "message": "Add a task to buy groceries",
  "conversation_id": "uuid-optional"  // null for new conversation
}

Response:
{
  "conversation_id": "uuid",
  "response": "I've added 'buy groceries' to your task list.",
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": {"title": "buy groceries"},
      "result": {"id": "uuid", "title": "buy groceries", "completed": false}
    }
  ]
}
```

**Alternatives Considered**:
- Separate endpoints for agent and conversation → Rejected (overcomplicates simple chat flow)
- GraphQL subscription for streaming → Deferred (not required for MVP)

---

## 5. Database Schema Extension

### Decision: Additive Schema with Conversation and Message Tables

**Rationale**: New tables for chat functionality without modifying existing Task table. Maintains Phase II compatibility.

**New Tables**:

1. **Conversation**
   - `id` (UUID, primary key)
   - `user_id` (string, foreign key reference, indexed)
   - `created_at` (timestamp)
   - `updated_at` (timestamp)

2. **Message**
   - `id` (UUID, primary key)
   - `conversation_id` (UUID, foreign key to Conversation)
   - `role` (enum: 'user' | 'assistant')
   - `content` (text)
   - `created_at` (timestamp)

3. **ToolCall**
   - `id` (UUID, primary key)
   - `message_id` (UUID, foreign key to Message)
   - `tool_name` (string)
   - `parameters` (JSON)
   - `result` (JSON)
   - `created_at` (timestamp)

**Migration Strategy**:
- SQLModel `create_all()` will create new tables without affecting existing `tasks` table
- No foreign key constraints to `tasks` table (tools reference by task ID at runtime)

**Alternatives Considered**:
- Single table with JSON message array → Rejected (poor query performance, harder to paginate)
- NoSQL document store → Rejected (violates technology stack constraints)

---

## 6. Frontend Chat UI Integration

### Decision: Floating Chat Button with Drawer/Modal using ChatKit

**Rationale**: Non-intrusive integration preserves Phase II layout. ChatKit provides ready-made components.

**UI Components**:

1. **ChatButton**: Fixed-position icon in bottom-right corner
2. **ChatDrawer**: Slide-out panel containing ChatKit conversation view
3. **ChatKit Integration**: Message list, input field, typing indicator

**State Management**:
- Local React state for chat open/closed
- API calls for sending messages
- Conversation ID stored in session for continuity

**Styling**:
- Tailwind CSS for positioning and animations
- ChatKit default theme (customizable via CSS variables)
- Responsive: full-screen on mobile, drawer on desktop

**Alternatives Considered**:
- Dedicated chat page → Rejected (loses context when navigating)
- Inline chat in sidebar → Rejected (requires layout modification)

---

## 7. Environment Variables

### Decision: Backend Owns All Secrets, Frontend Uses Public Key Only

**Rationale**: Follows Constitution constraints on secrets handling.

**Backend `.env`**:
```
OPENAI_API_KEY=sk-...         # OpenAI API authentication
BETTER_AUTH_SECRET=...        # JWT verification (existing)
BETTER_AUTH_URL=...           # Better Auth URL (existing)
DATABASE_URL=...              # Neon PostgreSQL (existing)
```

**Frontend `.env.local`**:
```
NEXT_PUBLIC_API_URL=...       # Backend API base URL (existing)
```

**Note**: `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` from user input is not standard OpenAI pattern. OpenAI ChatKit uses backend proxy for API calls, not direct frontend access. Frontend will call `/api/{user_id}/chat` endpoint.

**Alternatives Considered**:
- Direct OpenAI API calls from frontend → Rejected (exposes API key, violates security)

---

## 8. Error Handling Strategy

### Decision: Layered Error Translation with User-Friendly Messages

**Rationale**: Errors from different layers (DB, AI, tools) must be translated to safe, helpful user responses.

**Error Taxonomy**:

| Error Type | HTTP Status | User Message |
|------------|-------------|--------------|
| Unauthenticated | 401 | "Please log in to use the chat." |
| Unauthorized | 403 | "You don't have access to this resource." |
| Task Not Found | 404 | "I couldn't find that task. Want me to show your list?" |
| Invalid Input | 400 | "I didn't understand that. Could you rephrase?" |
| AI Service Error | 503 | "I'm having trouble right now. Please try again." |
| Database Error | 500 | "Something went wrong. Please try again." |

**Implementation**:
- Backend catches all errors, logs internally, returns safe message
- AI agent receives error context for generating helpful follow-up
- No stack traces or internal details exposed to user

---

## 9. Performance Targets

### Decision: Target Response Times Aligned with Success Criteria

| Operation | Target | Strategy |
|-----------|--------|----------|
| Add task via chat | < 5s | Optimize OpenAI call + single DB write |
| List tasks via chat | < 3s | Cached queries, pagination for large lists |
| Conversation load | < 1s | Load last 50 messages, paginate older |
| History persistence | Async | Write-behind after response sent |

**Optimizations**:
- Connection pooling for OpenAI API
- Async database operations with SQLModel
- Message batching for history writes

---

## 10. Security Considerations

### Decision: Defense in Depth with Multi-Layer Validation

**Security Layers**:

1. **Authentication**: JWT verification at endpoint level (existing)
2. **Authorization**: User ID validation from JWT, not request body
3. **Tool Isolation**: MCP tools receive user_id from backend context only
4. **Input Sanitization**: Pydantic validation on all inputs
5. **Output Filtering**: AI responses stripped of system details

**Threat Mitigations**:

| Threat | Mitigation |
|--------|------------|
| Cross-user data access | User ID from JWT, not user input |
| Prompt injection | Tool-only execution, no dynamic code |
| Information leakage | Error messages sanitized |
| Token theft | HTTPS required, short token expiry |

---

## Summary

All technical decisions have been made with Constitution compliance verified:

| Constitution Principle | Compliance |
|----------------------|------------|
| VII. Additive Extension | ✅ New tables, no modifications to Phase II |
| VIII. Architectural Authority | ✅ Agent → MCP → FastAPI → DB chain |
| IX. Stateless Server | ✅ Agent per request, DB persistence |
| X. MCP Tool Sovereignty | ✅ 5 single-purpose tools with user validation |
| XI. Agent Constraints | ✅ Tool-only execution, confirmation required |
| XII. Data Integrity | ✅ Transactional writes, error handling |
| XIII. Final Law | ✅ AI is assistant, backend is authority |

**Research Status**: ✅ Complete - Ready for Phase 1 Design
