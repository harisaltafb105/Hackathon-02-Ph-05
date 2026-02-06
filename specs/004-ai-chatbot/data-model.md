# Data Model: Phase III AI Chatbot

**Feature**: 004-ai-chatbot
**Date**: 2026-01-14
**Phase**: Phase 1 - Design

## Overview

This document defines the database schema extensions for the AI chatbot functionality. These tables are additive and do not modify the existing Phase II `tasks` table.

---

## Entity: Conversation

### Purpose

Represents a chat session for a user. Contains metadata about the conversation and provides a grouping for messages.

### Table Definition

**Table Name**: `conversations`

**SQLModel Class**:
```python
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from sqlalchemy import Index


class Conversation(SQLModel, table=True):
    """Conversation model representing a user's chat session."""

    __tablename__ = "conversations"

    # Primary key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique conversation identifier"
    )

    # User association
    user_id: str = Field(
        nullable=False,
        index=True,
        description="User ID from Better Auth JWT token"
    )

    # Conversation metadata
    title: str | None = Field(
        default=None,
        max_length=255,
        description="Optional conversation title (auto-generated from first message)"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Conversation creation timestamp"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last message timestamp"
    )

    # Indexes
    __table_args__ = (
        Index("idx_conv_user_id", "user_id"),
        Index("idx_conv_user_updated", "user_id", "updated_at"),
    )

    def update_timestamp(self):
        """Update the updated_at timestamp to current time."""
        self.updated_at = datetime.utcnow()
```

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Auto-generated unique identifier |
| `user_id` | VARCHAR | NOT NULL, INDEXED | Foreign key reference to Better Auth user |
| `title` | VARCHAR(255) | NULLABLE | Optional conversation title |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last activity timestamp |

### Relationships

- **User**: One user has many conversations (via `user_id`)
- **Messages**: One conversation has many messages (via `conversation_id` in Message)

### Indexes

1. **Primary Index**: `id` (UUID, clustered)
2. **User Index**: `user_id` (B-tree) - Fast filtering by user
3. **Composite Index**: `(user_id, updated_at)` - Fast sorted listings of recent conversations

---

## Entity: Message

### Purpose

Represents a single message in a conversation, either from the user or the AI assistant.

### Table Definition

**Table Name**: `messages`

**SQLModel Class**:
```python
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Column, Text
from sqlalchemy import Index


class MessageRole(str, Enum):
    """Message sender role."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(SQLModel, table=True):
    """Message model representing a single chat message."""

    __tablename__ = "messages"

    # Primary key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique message identifier"
    )

    # Conversation association
    conversation_id: UUID = Field(
        nullable=False,
        index=True,
        foreign_key="conversations.id",
        description="Parent conversation ID"
    )

    # Message content
    role: MessageRole = Field(
        nullable=False,
        description="Message sender role (user/assistant/system)"
    )

    content: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Message text content"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Message creation timestamp"
    )

    # Indexes
    __table_args__ = (
        Index("idx_msg_conversation_id", "conversation_id"),
        Index("idx_msg_conv_created", "conversation_id", "created_at"),
    )
```

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Auto-generated unique identifier |
| `conversation_id` | UUID | NOT NULL, FK, INDEXED | Reference to parent conversation |
| `role` | ENUM | NOT NULL | Message sender: user/assistant/system |
| `content` | TEXT | NOT NULL | Message text content |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Message timestamp |

### Relationships

- **Conversation**: Many messages belong to one conversation
- **ToolCalls**: One message (assistant) can have many tool calls

### Indexes

1. **Primary Index**: `id` (UUID, clustered)
2. **Conversation Index**: `conversation_id` (B-tree) - Fast message lookup
3. **Composite Index**: `(conversation_id, created_at)` - Ordered message retrieval

---

## Entity: ToolCall

### Purpose

Records an MCP tool invocation made by the AI assistant, including parameters and results for traceability.

### Table Definition

**Table Name**: `tool_calls`

**SQLModel Class**:
```python
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import JSONB


class ToolCall(SQLModel, table=True):
    """ToolCall model recording AI tool invocations."""

    __tablename__ = "tool_calls"

    # Primary key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique tool call identifier"
    )

    # Message association
    message_id: UUID = Field(
        nullable=False,
        index=True,
        foreign_key="messages.id",
        description="Parent message ID (assistant message)"
    )

    # Tool invocation details
    tool_name: str = Field(
        max_length=100,
        nullable=False,
        description="Name of the MCP tool invoked"
    )

    parameters: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, default={}),
        description="Tool input parameters"
    )

    result: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
        description="Tool execution result"
    )

    success: bool = Field(
        default=True,
        nullable=False,
        description="Whether tool execution succeeded"
    )

    error_message: str | None = Field(
        default=None,
        max_length=1000,
        description="Error message if execution failed"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Tool call timestamp"
    )

    # Indexes
    __table_args__ = (
        Index("idx_tc_message_id", "message_id"),
        Index("idx_tc_tool_name", "tool_name"),
    )
```

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Auto-generated unique identifier |
| `message_id` | UUID | NOT NULL, FK, INDEXED | Reference to assistant message |
| `tool_name` | VARCHAR(100) | NOT NULL | MCP tool name (e.g., add_task) |
| `parameters` | JSONB | NOT NULL, DEFAULT {} | Tool input parameters |
| `result` | JSONB | NULLABLE | Tool execution result |
| `success` | BOOLEAN | NOT NULL, DEFAULT TRUE | Execution success flag |
| `error_message` | VARCHAR(1000) | NULLABLE | Error details if failed |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Execution timestamp |

### Relationships

- **Message**: Many tool calls belong to one message

### Indexes

1. **Primary Index**: `id` (UUID, clustered)
2. **Message Index**: `message_id` (B-tree) - Tool calls per message
3. **Tool Name Index**: `tool_name` (B-tree) - Analytics/debugging queries

---

## Request/Response Schemas

### Chat Request Schema

```python
from pydantic import BaseModel, Field
from uuid import UUID


class ChatRequest(BaseModel):
    """Chat message request from frontend."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's chat message"
    )

    conversation_id: UUID | None = Field(
        default=None,
        description="Existing conversation ID (null for new conversation)"
    )
```

### Chat Response Schema

```python
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Any


class ToolCallResponse(BaseModel):
    """Tool call details in response."""

    tool: str = Field(..., description="Tool name")
    parameters: dict[str, Any] = Field(..., description="Tool parameters")
    result: dict[str, Any] | None = Field(None, description="Tool result")
    success: bool = Field(..., description="Execution success")


class ChatResponse(BaseModel):
    """Chat response to frontend."""

    conversation_id: UUID = Field(..., description="Conversation ID")
    response: str = Field(..., description="AI assistant response text")
    tool_calls: list[ToolCallResponse] = Field(
        default_factory=list,
        description="List of tool calls made"
    )
```

### Conversation List Response

```python
class ConversationSummary(BaseModel):
    """Conversation summary for listing."""

    id: UUID = Field(..., description="Conversation ID")
    title: str | None = Field(None, description="Conversation title")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last activity timestamp")
    message_count: int = Field(..., description="Number of messages")
```

### Message Response Schema

```python
class MessageResponse(BaseModel):
    """Message details for conversation history."""

    id: UUID = Field(..., description="Message ID")
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    created_at: datetime = Field(..., description="Message timestamp")
    tool_calls: list[ToolCallResponse] = Field(
        default_factory=list,
        description="Tool calls (if assistant message)"
    )

    class Config:
        from_attributes = True
```

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER (Better Auth)                        │
│                      (External - not stored)                     │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  │ user_id (string reference)
                                  │
    ┌─────────────────────────────┼─────────────────────────────┐
    │                             │                             │
    ▼                             ▼                             ▼
┌────────────┐             ┌──────────────┐             ┌──────────┐
│   TASKS    │             │ CONVERSATIONS│             │  (future │
│ (Phase II) │             │  (Phase III) │             │ entities)│
├────────────┤             ├──────────────┤             └──────────┘
│ id         │             │ id           │
│ title      │             │ user_id ─────┼──────┐
│ description│             │ title        │      │
│ completed  │             │ created_at   │      │
│ user_id    │             │ updated_at   │      │
│ created_at │             └──────┬───────┘      │
│ updated_at │                    │              │
└────────────┘                    │              │
                                  │ 1:N          │
                                  ▼              │
                         ┌──────────────┐        │
                         │   MESSAGES   │        │
                         ├──────────────┤        │
                         │ id           │        │
                         │ conversation_│◄───────┘
                         │   id         │
                         │ role         │
                         │ content      │
                         │ created_at   │
                         └──────┬───────┘
                                │
                                │ 1:N (only for assistant messages)
                                ▼
                         ┌──────────────┐
                         │  TOOL_CALLS  │
                         ├──────────────┤
                         │ id           │
                         │ message_id   │
                         │ tool_name    │
                         │ parameters   │
                         │ result       │
                         │ success      │
                         │ error_message│
                         │ created_at   │
                         └──────────────┘
```

---

## Migration Strategy

### Table Creation Order

1. `conversations` (no dependencies)
2. `messages` (depends on conversations)
3. `tool_calls` (depends on messages)

### Implementation

```python
# backend/models.py (additions)
# Add Conversation, Message, MessageRole, ToolCall classes

# backend/database.py (unchanged)
# SQLModel.metadata.create_all() will create new tables
```

### Rollback Strategy

```sql
-- If rollback needed (reverse order)
DROP TABLE IF EXISTS tool_calls;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS conversations;
```

---

## Data Integrity Constraints

### User Isolation

- Conversations filtered by `user_id` from JWT token
- Messages accessed only through parent conversation
- ToolCalls accessed only through parent message
- All queries include user context validation

### Cascade Behavior

- **Delete Conversation**: Cascade delete messages and tool_calls
- **Delete Message**: Cascade delete tool_calls
- **User Deletion**: Application handles cleanup (no FK to external user)

### Validation Rules

- `message.content` required, non-empty
- `tool_call.tool_name` must be valid MCP tool
- `conversation_id` must exist and belong to user
- `message_id` must exist and belong to user's conversation

---

## Performance Considerations

### Query Patterns

| Query | Index Used | Expected Performance |
|-------|------------|---------------------|
| List user's conversations | idx_conv_user_updated | < 10ms |
| Get conversation messages | idx_msg_conv_created | < 20ms |
| Get message tool calls | idx_tc_message_id | < 5ms |
| Insert new message | Primary key | < 10ms |

### Data Volume Estimates

- Messages per conversation: ~50 average
- Conversations per user: ~10 active
- Tool calls per message: 0-3
- Total messages: ~500 per active user

### Optimization Notes

- JSONB for parameters/result enables flexible schema
- Composite indexes for sorted listings
- Consider partitioning by user_id if scale exceeds 1M messages

---

## Summary

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `conversations` | Chat sessions | user_id, title, timestamps |
| `messages` | Chat messages | conversation_id, role, content |
| `tool_calls` | AI tool invocations | message_id, tool_name, params, result |

**Data Model Status**: ✅ Complete and ready for implementation
