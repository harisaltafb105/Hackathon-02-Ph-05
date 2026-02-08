"""
Pydantic schemas for request/response validation.
Defines data transfer objects for API endpoints.

Phase V: Extended with priority, tags, due_date, recurrence, reminders, pagination.
"""

import re
from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator, model_validator


# Tag validation regex: lowercase alphanumeric, hyphens, underscores
TAG_PATTERN = re.compile(r"^[a-z0-9_-]+$")


def normalize_tags(tags: list[str]) -> list[str]:
    """Normalize tags: lowercase, strip whitespace, remove invalid characters."""
    normalized = []
    for tag in tags:
        tag = tag.strip().lower()
        # Strip invalid characters
        tag = re.sub(r"[^a-z0-9_-]", "", tag)
        if tag and len(tag) <= 50:
            normalized.append(tag)
    return normalized[:20]  # Max 20 tags


class TaskResponse(BaseModel):
    """
    Task response schema.
    Used for GET, POST, PUT, PATCH responses.
    Phase V: Extended with priority, tags, due_date, is_overdue, recurrence fields.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: Optional[str]
    completed: bool
    priority: str = "none"
    tags: list[str] = []
    due_date: Optional[date] = None
    is_overdue: bool = False
    recurrence_rule: Optional[str] = None
    recurrence_group_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    user_id: str

    @model_validator(mode="after")
    def compute_overdue(self) -> "TaskResponse":
        """Compute is_overdue: true when due_date < today AND not completed."""
        if self.due_date and not self.completed and self.due_date < date.today():
            self.is_overdue = True
        else:
            self.is_overdue = False
        return self


class TaskCreate(BaseModel):
    """
    Task creation schema.
    Used for POST /api/{user_id}/tasks
    Phase V: Extended with priority, tags, due_date, recurrence_rule.
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

    priority: str = Field(
        default="none",
        description="Task priority (none, low, medium, high, urgent)"
    )

    tags: list[str] = Field(
        default_factory=list,
        description="Task tags (max 20 tags, each max 50 chars)"
    )

    due_date: Optional[date] = Field(
        default=None,
        description="Task due date (YYYY-MM-DD)"
    )

    recurrence_rule: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Recurrence rule (e.g., FREQ=DAILY)"
    )

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        valid = {"none", "low", "medium", "high", "urgent"}
        if v not in valid:
            raise ValueError(f"Priority must be one of: {', '.join(sorted(valid))}")
        return v

    @field_validator("tags")
    @classmethod
    def validate_and_normalize_tags(cls, v: list[str]) -> list[str]:
        return normalize_tags(v)


class TaskUpdate(BaseModel):
    """
    Task full update schema.
    Used for PUT /api/{user_id}/tasks/{task_id}
    All fields are required for PUT (full replacement).
    Phase V: Extended with priority, tags, due_date, recurrence_rule.
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

    priority: str = Field(
        default="none",
        description="Task priority (none, low, medium, high, urgent)"
    )

    tags: list[str] = Field(
        default_factory=list,
        description="Task tags"
    )

    due_date: Optional[date] = Field(
        default=None,
        description="Task due date (YYYY-MM-DD)"
    )

    recurrence_rule: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Recurrence rule"
    )

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        valid = {"none", "low", "medium", "high", "urgent"}
        if v not in valid:
            raise ValueError(f"Priority must be one of: {', '.join(sorted(valid))}")
        return v

    @field_validator("tags")
    @classmethod
    def validate_and_normalize_tags(cls, v: list[str]) -> list[str]:
        return normalize_tags(v)


class TaskPatch(BaseModel):
    """
    Task partial update schema.
    Used for PATCH /api/{user_id}/tasks/{task_id}
    All fields are optional for PATCH (partial update).
    Phase V: Extended with priority, tags, due_date, recurrence_rule.
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

    priority: Optional[str] = Field(
        default=None,
        description="Task priority (none, low, medium, high, urgent)"
    )

    tags: Optional[list[str]] = Field(
        default=None,
        description="Task tags (replaces existing tags)"
    )

    due_date: Optional[date] = Field(
        default=None,
        description="Task due date (YYYY-MM-DD)"
    )

    recurrence_rule: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Recurrence rule"
    )

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        valid = {"none", "low", "medium", "high", "urgent"}
        if v not in valid:
            raise ValueError(f"Priority must be one of: {', '.join(sorted(valid))}")
        return v

    @field_validator("tags")
    @classmethod
    def validate_and_normalize_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        if v is None:
            return v
        return normalize_tags(v)


# =============================================================================
# Phase V: Pagination, Reminder, and Tag Schemas
# =============================================================================


class PaginatedTaskResponse(BaseModel):
    """Paginated task list response."""
    tasks: list[TaskResponse]
    total: int
    limit: int
    offset: int


class ReminderCreate(BaseModel):
    """
    Reminder creation schema.
    Provide either trigger_at (absolute) or relative_to_due (relative).
    """
    trigger_at: Optional[datetime] = Field(
        default=None,
        description="Absolute trigger time (must be in the future)"
    )

    relative_to_due: Optional[str] = Field(
        default=None,
        description="Relative offset from due_date (e.g., '-1d', '-2d', '-1h')"
    )

    @model_validator(mode="after")
    def validate_reminder(self) -> "ReminderCreate":
        if not self.trigger_at and not self.relative_to_due:
            raise ValueError("Either trigger_at or relative_to_due must be provided")
        if self.trigger_at and self.relative_to_due:
            raise ValueError("Provide only one of trigger_at or relative_to_due")
        return self


class ReminderResponse(BaseModel):
    """Reminder response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    task_id: UUID
    user_id: str
    trigger_at: datetime
    status: str
    created_at: datetime


class TagListResponse(BaseModel):
    """List of distinct tags for the user."""
    tags: list[str]


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
