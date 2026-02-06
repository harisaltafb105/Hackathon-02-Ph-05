"""
MCP Tool Implementations for Phase III AI Chatbot.

This module implements the 5 MCP tools that wrap existing CRUD logic:
- add_task: Create a new task
- list_tasks: List tasks with optional filtering
- update_task: Update task title/description
- complete_task: Mark task as complete/incomplete
- delete_task: Delete a task

All tools enforce user isolation via ToolContext.

Contract Reference: specs/004-ai-chatbot/contracts/mcp-tools.md
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.models import Task


@dataclass
class ToolContext:
    """
    Context provided to all MCP tools.

    Enforces user isolation by providing user_id from JWT token,
    NOT from tool parameters.
    """
    user_id: str
    session: AsyncSession
    conversation_id: UUID


class ToolError:
    """Standardized error response for MCP tools."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    DATABASE_ERROR = "DATABASE_ERROR"

    @staticmethod
    def create(code: str, message: str, suggestion: str | None = None) -> dict[str, Any]:
        """Create a standardized error response."""
        error = {
            "error": True,
            "code": code,
            "message": message,
        }
        if suggestion:
            error["suggestion"] = suggestion
        return error


async def add_task(params: dict[str, Any], context: ToolContext) -> dict[str, Any]:
    """
    Create a new task for the authenticated user.

    Args:
        params: Tool parameters containing:
            - title (str, required): Task title (1-500 characters)
            - description (str, optional): Task description (max 5000 characters)
        context: Backend context including user_id from JWT

    Returns:
        Created task data or error response
    """
    try:
        # Validate title
        title = params.get("title", "").strip()
        if not title:
            return ToolError.create(
                ToolError.VALIDATION_ERROR,
                "Task title is required",
            )
        if len(title) > 500:
            return ToolError.create(
                ToolError.VALIDATION_ERROR,
                "Task title must be 500 characters or less",
            )

        # Validate description
        description = params.get("description")
        if description and len(description) > 5000:
            return ToolError.create(
                ToolError.VALIDATION_ERROR,
                "Task description must be 5000 characters or less",
            )

        # Create task with enforced user_id from context
        task = Task(
            title=title,
            description=description,
            user_id=context.user_id,  # Enforced from JWT, not user-provided
        )

        context.session.add(task)
        await context.session.commit()
        await context.session.refresh(task)

        return {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "created_at": task.created_at.isoformat(),
        }

    except Exception as e:
        await context.session.rollback()
        return ToolError.create(
            ToolError.DATABASE_ERROR,
            "Failed to create task. Please try again.",
        )


async def list_tasks(params: dict[str, Any], context: ToolContext) -> dict[str, Any]:
    """
    List tasks for the authenticated user with optional filtering.

    Args:
        params: Tool parameters containing:
            - status (str, optional): Filter by "all", "pending", or "completed"
            - limit (int, optional): Maximum tasks to return (default 50, max 100)
        context: Backend context including user_id from JWT

    Returns:
        List of tasks with counts or error response
    """
    try:
        status = params.get("status", "all")
        limit = min(params.get("limit", 50), 100)

        # Build query with user isolation
        query = select(Task).where(Task.user_id == context.user_id)

        # Apply status filter
        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)

        # Order by created_at descending and apply limit
        query = query.order_by(Task.created_at.desc()).limit(limit)

        result = await context.session.execute(query)
        tasks = result.scalars().all()

        # Get counts
        all_query = select(Task).where(Task.user_id == context.user_id)
        all_result = await context.session.execute(all_query)
        all_tasks = all_result.scalars().all()

        pending_count = sum(1 for t in all_tasks if not t.completed)
        completed_count = sum(1 for t in all_tasks if t.completed)

        return {
            "tasks": [
                {
                    "id": str(t.id),
                    "title": t.title,
                    "completed": t.completed,
                    "created_at": t.created_at.isoformat(),
                }
                for t in tasks
            ],
            "count": len(tasks),
            "pending_count": pending_count,
            "completed_count": completed_count,
        }

    except Exception as e:
        return ToolError.create(
            ToolError.DATABASE_ERROR,
            "Failed to retrieve tasks. Please try again.",
        )


async def update_task(params: dict[str, Any], context: ToolContext) -> dict[str, Any]:
    """
    Update an existing task's title or description.

    Args:
        params: Tool parameters containing:
            - task_id (str, required): UUID of the task to update
            - title (str, optional): New task title
            - description (str, optional): New task description
        context: Backend context including user_id from JWT

    Returns:
        Updated task data or error response
    """
    try:
        task_id = params.get("task_id")
        if not task_id:
            return ToolError.create(
                ToolError.VALIDATION_ERROR,
                "Task ID is required",
            )

        # Parse UUID
        try:
            task_uuid = UUID(task_id)
        except ValueError:
            return ToolError.create(
                ToolError.VALIDATION_ERROR,
                "Invalid task ID format",
            )

        # Check if at least one field is being updated
        title = params.get("title")
        description = params.get("description")

        if title is None and description is None:
            return ToolError.create(
                ToolError.VALIDATION_ERROR,
                "Please specify what to update (title or description)",
            )

        # Validate fields
        if title is not None:
            title = title.strip()
            if not title:
                return ToolError.create(
                    ToolError.VALIDATION_ERROR,
                    "Task title cannot be empty",
                )
            if len(title) > 500:
                return ToolError.create(
                    ToolError.VALIDATION_ERROR,
                    "Task title must be 500 characters or less",
                )

        if description is not None and len(description) > 5000:
            return ToolError.create(
                ToolError.VALIDATION_ERROR,
                "Task description must be 5000 characters or less",
            )

        # Find task with user isolation
        query = select(Task).where(
            Task.id == task_uuid,
            Task.user_id == context.user_id,
        )
        result = await context.session.execute(query)
        task = result.scalars().first()

        if not task:
            return ToolError.create(
                ToolError.NOT_FOUND,
                "Task not found. Would you like to see your current tasks?",
                suggestion="list_tasks",
            )

        # Update fields
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description

        task.update_timestamp()

        context.session.add(task)
        await context.session.commit()
        await context.session.refresh(task)

        return {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "updated_at": task.updated_at.isoformat(),
        }

    except Exception as e:
        await context.session.rollback()
        return ToolError.create(
            ToolError.DATABASE_ERROR,
            "Failed to update task. Please try again.",
        )


async def complete_task(params: dict[str, Any], context: ToolContext) -> dict[str, Any]:
    """
    Mark a task as completed or uncompleted.

    Args:
        params: Tool parameters containing:
            - task_id (str, required): UUID of the task to complete
            - completed (bool, optional): Completion status (default True)
        context: Backend context including user_id from JWT

    Returns:
        Updated task data or error response
    """
    try:
        task_id = params.get("task_id")
        if not task_id:
            return ToolError.create(
                ToolError.VALIDATION_ERROR,
                "Task ID is required",
            )

        # Parse UUID
        try:
            task_uuid = UUID(task_id)
        except ValueError:
            return ToolError.create(
                ToolError.VALIDATION_ERROR,
                "Invalid task ID format",
            )

        completed = params.get("completed", True)

        # Find task with user isolation
        query = select(Task).where(
            Task.id == task_uuid,
            Task.user_id == context.user_id,
        )
        result = await context.session.execute(query)
        task = result.scalars().first()

        if not task:
            return ToolError.create(
                ToolError.NOT_FOUND,
                "Task not found. Would you like to see your current tasks?",
                suggestion="list_tasks",
            )

        # Check if already in desired state
        if task.completed == completed:
            status_text = "complete" if completed else "incomplete"
            return ToolError.create(
                ToolError.VALIDATION_ERROR,
                f"This task is already marked as {status_text}.",
            )

        # Update completion status
        task.completed = completed
        task.update_timestamp()

        context.session.add(task)
        await context.session.commit()
        await context.session.refresh(task)

        return {
            "id": str(task.id),
            "title": task.title,
            "completed": task.completed,
            "updated_at": task.updated_at.isoformat(),
        }

    except Exception as e:
        await context.session.rollback()
        return ToolError.create(
            ToolError.DATABASE_ERROR,
            "Failed to update task. Please try again.",
        )


async def delete_task(params: dict[str, Any], context: ToolContext) -> dict[str, Any]:
    """
    Permanently delete a task.

    Args:
        params: Tool parameters containing:
            - task_id (str, required): UUID of the task to delete
        context: Backend context including user_id from JWT

    Returns:
        Deletion confirmation or error response
    """
    try:
        task_id = params.get("task_id")
        if not task_id:
            return ToolError.create(
                ToolError.VALIDATION_ERROR,
                "Task ID is required",
            )

        # Parse UUID
        try:
            task_uuid = UUID(task_id)
        except ValueError:
            return ToolError.create(
                ToolError.VALIDATION_ERROR,
                "Invalid task ID format",
            )

        # Find task with user isolation
        query = select(Task).where(
            Task.id == task_uuid,
            Task.user_id == context.user_id,
        )
        result = await context.session.execute(query)
        task = result.scalars().first()

        if not task:
            return ToolError.create(
                ToolError.NOT_FOUND,
                "Task not found. It may have already been deleted.",
            )

        # Store title for confirmation
        task_title = task.title

        # Delete the task
        await context.session.delete(task)
        await context.session.commit()

        return {
            "deleted": True,
            "task_id": str(task_uuid),
            "title": task_title,
        }

    except Exception as e:
        await context.session.rollback()
        return ToolError.create(
            ToolError.DATABASE_ERROR,
            "Failed to delete task. Please try again.",
        )


def get_tool_definitions() -> list[dict[str, Any]]:
    """
    Get OpenAI function definitions for all MCP tools.

    Returns:
        List of tool definitions for OpenAI function calling
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Creates a new task for the user's todo list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Task title (required, 1-500 characters)",
                            "minLength": 1,
                            "maxLength": 500,
                        },
                        "description": {
                            "type": "string",
                            "description": "Task description (optional, max 5000 characters)",
                            "maxLength": 5000,
                        },
                    },
                    "required": ["title"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "Lists user's tasks with optional filtering",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "completed"],
                            "default": "all",
                            "description": "Filter by completion status",
                        },
                        "limit": {
                            "type": "integer",
                            "default": 50,
                            "maximum": 100,
                            "description": "Maximum number of tasks to return",
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Updates a task's title or description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "ID of the task to update",
                        },
                        "title": {
                            "type": "string",
                            "description": "New task title (optional)",
                            "minLength": 1,
                            "maxLength": 500,
                        },
                        "description": {
                            "type": "string",
                            "description": "New task description (optional)",
                            "maxLength": 5000,
                        },
                    },
                    "required": ["task_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Marks a task as completed",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "ID of the task to complete",
                        },
                        "completed": {
                            "type": "boolean",
                            "default": True,
                            "description": "Completion status (true to complete, false to uncomplete)",
                        },
                    },
                    "required": ["task_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Permanently deletes a task from the user's list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "ID of the task to delete",
                        },
                    },
                    "required": ["task_id"],
                },
            },
        },
    ]


# Tool registry for dynamic lookup
TOOL_REGISTRY = {
    "add_task": add_task,
    "list_tasks": list_tasks,
    "update_task": update_task,
    "complete_task": complete_task,
    "delete_task": delete_task,
}


async def execute_tool(tool_name: str, params: dict[str, Any], context: ToolContext) -> dict[str, Any]:
    """
    Execute a tool by name.

    Args:
        tool_name: Name of the tool to execute
        params: Tool parameters
        context: Execution context

    Returns:
        Tool result or error
    """
    tool_fn = TOOL_REGISTRY.get(tool_name)
    if not tool_fn:
        return ToolError.create(
            ToolError.VALIDATION_ERROR,
            f"Unknown tool: {tool_name}",
        )

    return await tool_fn(params, context)
