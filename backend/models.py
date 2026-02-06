"""
SQLModel database models.
Defines the User, Task, Conversation, Message, and ToolCall models.

Phase II: User, Task
Phase III: Conversation, Message, ToolCall (AI Chatbot)
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Column, String, Text
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import JSONB


class User(SQLModel, table=True):
    """
    User model for authentication.
    Stores user credentials and profile information.
    """

    __tablename__ = "users"

    # Primary key - auto-generated UUID
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False
    )

    # User credentials
    email: str = Field(
        max_length=255,
        nullable=False,
        unique=True,
        index=True,
        description="User email (unique, used for login)"
    )

    password_hash: str = Field(
        max_length=255,
        nullable=False,
        description="Hashed password (bcrypt)"
    )

    # User profile
    name: str = Field(
        max_length=255,
        nullable=False,
        description="User display name"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when user was created"
    )

    # Define indexes
    __table_args__ = (
        Index("idx_email", "email", unique=True),
    )


class Task(SQLModel, table=True):
    """
    Task model representing a user's todo item.

    All tasks are scoped to a user via user_id foreign key.
    This enforces strict user isolation at the database level.
    """

    __tablename__ = "tasks"

    # Primary key - auto-generated UUID
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False
    )

    # Task fields
    title: str = Field(
        max_length=500,
        nullable=False,
        description="Task title (required, 1-500 characters)"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        sa_column=Column(String(5000), nullable=True),
        description="Task description (optional, max 5000 characters)"
    )

    completed: bool = Field(
        default=False,
        nullable=False,
        description="Task completion status"
    )

    # Timestamps - auto-managed
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when task was created"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when task was last updated"
    )

    # Foreign key to user (managed by Better Auth, not in our database)
    user_id: str = Field(
        nullable=False,
        index=True,
        description="User ID from Better Auth JWT token"
    )

    # Define indexes for performance
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_user_created", "user_id", "created_at"),
    )

    def update_timestamp(self):
        """
        Update the updated_at timestamp to current time.
        Call this before saving after modifications.
        """
        self.updated_at = datetime.utcnow()


# =============================================================================
# Phase III: AI Chatbot Models
# =============================================================================


class MessageRole(str, Enum):
    """Message sender role for chat conversations."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Conversation(SQLModel, table=True):
    """
    Conversation model representing a user's chat session.

    Contains metadata about the conversation and provides
    a grouping for messages.

    Data Model Reference: specs/004-ai-chatbot/data-model.md
    """

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
    title: Optional[str] = Field(
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


class Message(SQLModel, table=True):
    """
    Message model representing a single chat message.

    Either from the user or the AI assistant.

    Data Model Reference: specs/004-ai-chatbot/data-model.md
    """

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


class ToolCall(SQLModel, table=True):
    """
    ToolCall model recording AI tool invocations.

    Tracks MCP tool calls made by the AI assistant for
    traceability and debugging.

    Data Model Reference: specs/004-ai-chatbot/data-model.md
    """

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

    result: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
        description="Tool execution result"
    )

    success: bool = Field(
        default=True,
        nullable=False,
        description="Whether tool execution succeeded"
    )

    error_message: Optional[str] = Field(
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
