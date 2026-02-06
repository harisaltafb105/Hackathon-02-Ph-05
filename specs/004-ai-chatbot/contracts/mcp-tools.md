# MCP Tool Contracts: Phase III AI Chatbot

**Feature**: 004-ai-chatbot
**Date**: 2026-01-14
**Version**: 1.0.0

## Overview

This document defines the MCP (Model Context Protocol) tool interfaces that the AI agent uses to interact with the Todo application backend. Each tool is stateless, single-purpose, and enforces user isolation.

---

## Tool: add_task

### Purpose
Creates a new task for the authenticated user.

### Input Schema
```json
{
  "name": "add_task",
  "description": "Creates a new task for the user's todo list",
  "parameters": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "Task title (required, 1-500 characters)",
        "minLength": 1,
        "maxLength": 500
      },
      "description": {
        "type": "string",
        "description": "Task description (optional, max 5000 characters)",
        "maxLength": 5000
      }
    },
    "required": ["title"]
  }
}
```

### Output Schema
```json
{
  "type": "object",
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "title": { "type": "string" },
    "description": { "type": "string", "nullable": true },
    "completed": { "type": "boolean" },
    "created_at": { "type": "string", "format": "date-time" }
  }
}
```

### Example
```
Input: {"title": "Buy groceries", "description": "Milk, eggs, bread"}
Output: {"id": "uuid", "title": "Buy groceries", "description": "Milk, eggs, bread", "completed": false, "created_at": "2026-01-14T10:30:00Z"}
```

### Error Cases
| Error | Message |
|-------|---------|
| Empty title | "Task title is required" |
| Title too long | "Task title must be 500 characters or less" |
| Database error | "Failed to create task. Please try again." |

---

## Tool: list_tasks

### Purpose
Retrieves all tasks for the authenticated user, with optional filtering.

### Input Schema
```json
{
  "name": "list_tasks",
  "description": "Lists user's tasks with optional filtering",
  "parameters": {
    "type": "object",
    "properties": {
      "status": {
        "type": "string",
        "enum": ["all", "pending", "completed"],
        "default": "all",
        "description": "Filter by completion status"
      },
      "limit": {
        "type": "integer",
        "default": 50,
        "maximum": 100,
        "description": "Maximum number of tasks to return"
      }
    },
    "required": []
  }
}
```

### Output Schema
```json
{
  "type": "object",
  "properties": {
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string", "format": "uuid" },
          "title": { "type": "string" },
          "completed": { "type": "boolean" },
          "created_at": { "type": "string", "format": "date-time" }
        }
      }
    },
    "count": { "type": "integer" },
    "pending_count": { "type": "integer" },
    "completed_count": { "type": "integer" }
  }
}
```

### Example
```
Input: {"status": "pending"}
Output: {
  "tasks": [
    {"id": "uuid1", "title": "Buy groceries", "completed": false, "created_at": "2026-01-14T10:30:00Z"},
    {"id": "uuid2", "title": "Call mom", "completed": false, "created_at": "2026-01-14T09:00:00Z"}
  ],
  "count": 2,
  "pending_count": 2,
  "completed_count": 3
}
```

### Error Cases
| Error | Message |
|-------|---------|
| Database error | "Failed to retrieve tasks. Please try again." |

---

## Tool: update_task

### Purpose
Updates an existing task's title or description.

### Input Schema
```json
{
  "name": "update_task",
  "description": "Updates a task's title or description",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "format": "uuid",
        "description": "ID of the task to update"
      },
      "title": {
        "type": "string",
        "description": "New task title (optional)",
        "minLength": 1,
        "maxLength": 500
      },
      "description": {
        "type": "string",
        "description": "New task description (optional)",
        "maxLength": 5000
      }
    },
    "required": ["task_id"]
  }
}
```

### Output Schema
```json
{
  "type": "object",
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "title": { "type": "string" },
    "description": { "type": "string", "nullable": true },
    "completed": { "type": "boolean" },
    "updated_at": { "type": "string", "format": "date-time" }
  }
}
```

### Example
```
Input: {"task_id": "uuid1", "title": "Buy groceries and snacks"}
Output: {"id": "uuid1", "title": "Buy groceries and snacks", "description": null, "completed": false, "updated_at": "2026-01-14T11:00:00Z"}
```

### Error Cases
| Error | Message |
|-------|---------|
| Task not found | "Task not found. Would you like to see your current tasks?" |
| Invalid task_id | "Invalid task ID format" |
| No fields provided | "Please specify what to update (title or description)" |
| Title too long | "Task title must be 500 characters or less" |

---

## Tool: complete_task

### Purpose
Marks a task as completed (or toggles completion status).

### Input Schema
```json
{
  "name": "complete_task",
  "description": "Marks a task as completed",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "format": "uuid",
        "description": "ID of the task to complete"
      },
      "completed": {
        "type": "boolean",
        "default": true,
        "description": "Completion status (true to complete, false to uncomplete)"
      }
    },
    "required": ["task_id"]
  }
}
```

### Output Schema
```json
{
  "type": "object",
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "title": { "type": "string" },
    "completed": { "type": "boolean" },
    "updated_at": { "type": "string", "format": "date-time" }
  }
}
```

### Example
```
Input: {"task_id": "uuid1", "completed": true}
Output: {"id": "uuid1", "title": "Buy groceries", "completed": true, "updated_at": "2026-01-14T12:00:00Z"}
```

### Error Cases
| Error | Message |
|-------|---------|
| Task not found | "Task not found. Would you like to see your current tasks?" |
| Already completed | "This task is already marked as complete." |
| Invalid task_id | "Invalid task ID format" |

---

## Tool: delete_task

### Purpose
Permanently deletes a task.

### Input Schema
```json
{
  "name": "delete_task",
  "description": "Permanently deletes a task from the user's list",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "format": "uuid",
        "description": "ID of the task to delete"
      }
    },
    "required": ["task_id"]
  }
}
```

### Output Schema
```json
{
  "type": "object",
  "properties": {
    "deleted": { "type": "boolean" },
    "task_id": { "type": "string", "format": "uuid" },
    "title": { "type": "string", "description": "Title of deleted task for confirmation" }
  }
}
```

### Example
```
Input: {"task_id": "uuid1"}
Output: {"deleted": true, "task_id": "uuid1", "title": "Buy groceries"}
```

### Error Cases
| Error | Message |
|-------|---------|
| Task not found | "Task not found. It may have already been deleted." |
| Invalid task_id | "Invalid task ID format" |

---

## User Isolation Enforcement

All tools receive `user_id` from the backend context (extracted from JWT), NOT from tool parameters.

### Implementation Pattern

```python
async def add_task(params: dict, context: ToolContext) -> dict:
    """
    MCP tool implementation with user isolation.

    Args:
        params: Tool parameters from AI agent
        context: Backend context including user_id from JWT

    Returns:
        Tool result or error
    """
    user_id = context.user_id  # From JWT, NOT from params

    # Create task with enforced user_id
    task = Task(
        title=params["title"],
        description=params.get("description"),
        user_id=user_id  # Enforced, not user-provided
    )

    # Save to database
    ...

    return task.model_dump()
```

### Context Object

```python
@dataclass
class ToolContext:
    """Context provided to all MCP tools."""
    user_id: str          # From JWT token
    session: AsyncSession  # Database session
    conversation_id: UUID  # Current conversation
```

---

## Error Handling Contract

### Error Response Format

```json
{
  "error": true,
  "code": "TASK_NOT_FOUND",
  "message": "Task not found. Would you like to see your current tasks?",
  "suggestion": "list_tasks"
}
```

### Error Codes

| Code | HTTP Equivalent | Description |
|------|-----------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid input parameters |
| `NOT_FOUND` | 404 | Resource doesn't exist |
| `DATABASE_ERROR` | 500 | Database operation failed |

### AI Agent Error Handling

The AI agent should:
1. Receive error response from tool
2. Generate user-friendly message based on error
3. Optionally suggest follow-up action
4. Never expose error codes or internal details to user

---

## Tool Registration

Tools are registered with the OpenAI Agents SDK as functions:

```python
from openai import OpenAI

agent_tools = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Creates a new task for the user's todo list",
            "parameters": { ... }  # From schema above
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "Lists user's tasks with optional filtering",
            "parameters": { ... }
        }
    },
    # ... other tools
]
```

---

## Summary

| Tool | Operation | Required Params | Optional Params |
|------|-----------|-----------------|-----------------|
| `add_task` | Create | title | description |
| `list_tasks` | Read | - | status, limit |
| `update_task` | Update | task_id | title, description |
| `complete_task` | Update | task_id | completed |
| `delete_task` | Delete | task_id | - |

**Contract Status**: ✅ Complete and ready for implementation
