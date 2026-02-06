"""
Pydantic schemas for request/response validation.
Defines data transfer objects for API endpoints.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class TaskResponse(BaseModel):
    """
    Task response schema.
    Used for GET, POST, PUT, PATCH responses.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
    user_id: str


class TaskCreate(BaseModel):
    """
    Task creation schema.
    Used for POST /api/{user_id}/tasks
    """
    title: str = Field(
        min_length=1,
        max_length=500,
        description="Task title (required, 1-500 characters)"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Task description (optional, max 5000 characters)"
    )


class TaskUpdate(BaseModel):
    """
    Task full update schema.
    Used for PUT /api/{user_id}/tasks/{task_id}
    All fields are required for PUT (full replacement).
    """
    title: str = Field(
        min_length=1,
        max_length=500,
        description="Task title (required)"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Task description (optional)"
    )

    completed: bool = Field(
        description="Task completion status (required)"
    )


class TaskPatch(BaseModel):
    """
    Task partial update schema.
    Used for PATCH /api/{user_id}/tasks/{task_id}
    All fields are optional for PATCH (partial update).
    """
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="Task title (optional)"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Task description (optional)"
    )

    completed: Optional[bool] = Field(
        default=None,
        description="Task completion status (optional)"
    )


# Authentication Schemas

class UserRegister(BaseModel):
    """
    User registration schema.
    Used for POST /auth/register
    """
    email: EmailStr = Field(
        description="User email address"
    )

    password: str = Field(
        min_length=8,
        max_length=100,
        description="User password (min 8 characters)"
    )

    name: str = Field(
        min_length=1,
        max_length=255,
        description="User display name"
    )


class UserLogin(BaseModel):
    """
    User login schema.
    Used for POST /auth/login
    """
    email: EmailStr = Field(
        description="User email address"
    )

    password: str = Field(
        description="User password"
    )


class UserResponse(BaseModel):
    """
    User response schema (without password).
    Used in authentication responses.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: str
    created_at: datetime


class AuthResponse(BaseModel):
    """
    Authentication response schema.
    Returned on successful login/register.
    """
    user: UserResponse
    token: str = Field(
        description="JWT authentication token"
    )


# =============================================================================
# Phase III: AI Chatbot Schemas
# Contract Reference: specs/004-ai-chatbot/contracts/chat-api.yaml
# =============================================================================


class ChatRequest(BaseModel):
    """
    Chat message request from frontend.
    Used for POST /api/{user_id}/chat
    """
    message: str = Field(
        min_length=1,
        max_length=10000,
        description="User's chat message"
    )

    conversation_id: Optional[UUID] = Field(
        default=None,
        description="Existing conversation ID (null for new conversation)"
    )


class ToolCallResponse(BaseModel):
    """
    Tool call details in response.
    """
    tool: str = Field(
        description="Tool name"
    )

    parameters: dict = Field(
        description="Tool parameters"
    )

    result: Optional[dict] = Field(
        default=None,
        description="Tool result"
    )

    success: bool = Field(
        description="Execution success"
    )


class ChatResponse(BaseModel):
    """
    Chat response to frontend.
    """
    conversation_id: UUID = Field(
        description="Conversation ID"
    )

    response: str = Field(
        description="AI assistant response text"
    )

    tool_calls: list[ToolCallResponse] = Field(
        default_factory=list,
        description="List of tool calls made"
    )


class ConversationSummary(BaseModel):
    """
    Conversation summary for listing.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        description="Conversation ID"
    )

    title: Optional[str] = Field(
        default=None,
        description="Conversation title"
    )

    created_at: datetime = Field(
        description="Creation timestamp"
    )

    updated_at: datetime = Field(
        description="Last activity timestamp"
    )

    message_count: int = Field(
        description="Number of messages"
    )


class ConversationListResponse(BaseModel):
    """
    Paginated list of conversations.
    """
    conversations: list[ConversationSummary] = Field(
        description="List of conversations"
    )

    total: int = Field(
        description="Total number of conversations"
    )

    limit: int = Field(
        description="Page size"
    )

    offset: int = Field(
        description="Page offset"
    )


class MessageResponse(BaseModel):
    """
    Message details for conversation history.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        description="Message ID"
    )

    role: str = Field(
        description="Message role (user/assistant)"
    )

    content: str = Field(
        description="Message content"
    )

    created_at: datetime = Field(
        description="Message timestamp"
    )

    tool_calls: list[ToolCallResponse] = Field(
        default_factory=list,
        description="Tool calls (if assistant message)"
    )


class ConversationDetailResponse(BaseModel):
    """
    Conversation with messages.
    """
    id: UUID = Field(
        description="Conversation ID"
    )

    title: Optional[str] = Field(
        default=None,
        description="Conversation title"
    )

    created_at: datetime = Field(
        description="Creation timestamp"
    )

    updated_at: datetime = Field(
        description="Last activity timestamp"
    )

    messages: list[MessageResponse] = Field(
        description="List of messages"
    )

    has_more: bool = Field(
        default=False,
        description="Whether more messages exist before the oldest returned"
    )
