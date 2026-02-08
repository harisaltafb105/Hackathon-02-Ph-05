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

from backend.models import Task, Reminder, ReminderStatus
from backend.schemas import normalize_tags


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

        # Phase V: Extract new fields
        priority = params.get("priority", "none")
        valid_priorities = {"none", "low", "medium", "high", "urgent"}
        if priority not in valid_priorities:
            return ToolError.create(
                ToolError.VALIDATION_ERROR,
                f"Invalid priority. Must be one of: {', '.join(sorted(valid_priorities))}",
            )

        tags = params.get("tags", [])
        if isinstance(tags, list):
            tags = normalize_tags(tags)

        due_date = params.get("due_date")
        recurrence_rule = params.get("recurrence_rule")

        # Create task with enforced user_id from context
        from datetime import date as date_type
        from uuid import uuid4 as gen_uuid

        task = Task(
            title=title,
            description=description,
            user_id=context.user_id,
            priority=priority,
            tags=tags,
            due_date=date_type.fromisoformat(due_date) if due_date else None,
            recurrence_rule=recurrence_rule,
        )

        if recurrence_rule:
            task.recurrence_group_id = gen_uuid()

        context.session.add(task)
        await context.session.commit()
        await context.session.refresh(task)

        return {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority,
            "tags": task.tags,
            "due_date": str(task.due_date) if task.due_date else None,
            "recurrence_rule": task.recurrence_rule,
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
            - q (str, optional): Keyword search on title/description
            - priority (str, optional): Filter by priority (comma-separated)
            - tag (str, optional): Filter by tag (comma-separated)
            - sort_by (str, optional): Sort field
            - overdue (bool, optional): Filter overdue tasks
        context: Backend context including user_id from JWT

    Returns:
        List of tasks with counts or error response
    """
    try:
        from datetime import date as date_type
        from sqlalchemy import case as sql_case

        status = params.get("status", "all")
        limit = min(params.get("limit", 50), 100)

        # Build query with user isolation
        query = select(Task).where(Task.user_id == context.user_id)

        # Apply status filter
        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)

        # Phase V: Search
        q = params.get("q")
        if q:
            pattern = f"%{q}%"
            query = query.where(
                (Task.title.ilike(pattern)) | (Task.description.ilike(pattern))
            )

        # Phase V: Priority filter
        priority_filter = params.get("priority")
        if priority_filter:
            priorities = [p.strip() for p in priority_filter.split(",") if p.strip()]
            if priorities:
                query = query.where(Task.priority.in_(priorities))

        # Phase V: Tag filter
        tag_filter = params.get("tag")
        if tag_filter:
            tags = [t.strip().lower() for t in tag_filter.split(",") if t.strip()]
            for t in tags:
                query = query.where(Task.tags.contains([t]))

        # Phase V: Overdue filter
        overdue = params.get("overdue")
        if overdue:
            query = query.where(
                Task.completed == False,
                Task.due_date < date_type.today(),
                Task.due_date.isnot(None),
            )

        # Phase V: Sort
        sort_by = params.get("sort_by", "created_at")
        if sort_by == "priority":
            priority_order = sql_case(
                (Task.priority == "urgent", 4),
                (Task.priority == "high", 3),
                (Task.priority == "medium", 2),
                (Task.priority == "low", 1),
                else_=0,
            )
            query = query.order_by(priority_order.desc())
        elif sort_by == "due_date":
            query = query.order_by(Task.due_date.asc().nulls_last())
        else:
            query = query.order_by(Task.created_at.desc())

        query = query.limit(limit)

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
                    "priority": t.priority,
                    "tags": t.tags or [],
                    "due_date": str(t.due_date) if t.due_date else None,
                    "is_overdue": (
                        t.due_date is not None
                        and not t.completed
                        and t.due_date < date_type.today()
                    ),
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
        priority = params.get("priority")
        tags = params.get("tags")
        due_date = params.get("due_date")

        if all(v is None for v in [title, description, priority, tags, due_date]):
            return ToolError.create(
                ToolError.VALIDATION_ERROR,
                "Please specify what to update (title, description, priority, tags, or due_date)",
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
        if priority is not None:
            valid_priorities = {"none", "low", "medium", "high", "urgent"}
            if priority not in valid_priorities:
                return ToolError.create(
                    ToolError.VALIDATION_ERROR,
                    f"Invalid priority. Must be one of: {', '.join(sorted(valid_priorities))}",
                )
            task.priority = priority
        if tags is not None:
            if isinstance(tags, list):
                task.tags = normalize_tags(tags)
        if due_date is not None:
            from datetime import date as date_type
            try:
                task.due_date = date_type.fromisoformat(due_date) if due_date else None
            except ValueError:
                return ToolError.create(
                    ToolError.VALIDATION_ERROR,
                    "Invalid date format. Use YYYY-MM-DD.",
                )

        task.update_timestamp()

        context.session.add(task)
        await context.session.commit()
        await context.session.refresh(task)

        return {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority,
            "tags": task.tags or [],
            "due_date": str(task.due_date) if task.due_date else None,
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

        new_instance_info = None

        if completed:
            # Cancel pending reminders
            reminder_query = select(Reminder).where(
                Reminder.task_id == task_uuid,
                Reminder.status == ReminderStatus.PENDING.value,
            )
            reminder_result = await context.session.execute(reminder_query)
            for r in reminder_result.scalars().all():
                r.status = ReminderStatus.CANCELLED.value
                context.session.add(r)

            # Generate next recurring instance
            if task.recurrence_rule:
                from backend.services.recurrence import generate_next_instance
                new_task = await generate_next_instance(task, context.session)
                if new_task:
                    new_instance_info = {
                        "id": str(new_task.id),
                        "title": new_task.title,
                        "due_date": str(new_task.due_date) if new_task.due_date else None,
                    }

        context.session.add(task)
        await context.session.commit()
        await context.session.refresh(task)

        result = {
            "id": str(task.id),
            "title": task.title,
            "completed": task.completed,
            "updated_at": task.updated_at.isoformat(),
        }
        if new_instance_info:
            result["next_instance"] = new_instance_info
        return result

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


async def set_reminder(params: dict[str, Any], context: ToolContext) -> dict[str, Any]:
    """
    Create a reminder for a task.

    Args:
        params: Tool parameters containing:
            - task_id (str, required): UUID of the task
            - trigger_at (str, optional): Absolute datetime (ISO format)
            - relative_to_due (str, optional): Relative offset (e.g., "-1d", "-2h")
        context: Backend context including user_id from JWT

    Returns:
        Created reminder data or error response
    """
    try:
        task_id = params.get("task_id")
        if not task_id:
            return ToolError.create(ToolError.VALIDATION_ERROR, "Task ID is required")

        try:
            task_uuid = UUID(task_id)
        except ValueError:
            return ToolError.create(ToolError.VALIDATION_ERROR, "Invalid task ID format")

        # Find task with user isolation
        query = select(Task).where(Task.id == task_uuid, Task.user_id == context.user_id)
        result = await context.session.execute(query)
        task = result.scalars().first()

        if not task:
            return ToolError.create(ToolError.NOT_FOUND, "Task not found.")

        trigger_at_str = params.get("trigger_at")
        relative = params.get("relative_to_due")

        if not trigger_at_str and not relative:
            return ToolError.create(
                ToolError.VALIDATION_ERROR,
                "Provide either trigger_at (datetime) or relative_to_due (e.g., '-1d')",
            )

        import re
        from datetime import timedelta

        if trigger_at_str:
            trigger_at = datetime.fromisoformat(trigger_at_str.replace("Z", "+00:00")).replace(tzinfo=None)
        else:
            if not task.due_date:
                return ToolError.create(
                    ToolError.VALIDATION_ERROR,
                    "Task has no due date. Use absolute trigger_at instead.",
                )
            match = re.match(r"^-(\d+)([dh])$", relative)
            if not match:
                return ToolError.create(
                    ToolError.VALIDATION_ERROR,
                    "Invalid format. Use '-Nd' or '-Nh' (e.g., '-1d', '-2h')",
                )
            amount, unit = int(match.group(1)), match.group(2)
            base = datetime(task.due_date.year, task.due_date.month, task.due_date.day, 9, 0, 0)
            if unit == "d":
                trigger_at = base - timedelta(days=amount)
            else:
                trigger_at = base - timedelta(hours=amount)

        if trigger_at <= datetime.utcnow():
            return ToolError.create(
                ToolError.VALIDATION_ERROR,
                "Reminder time must be in the future",
            )

        reminder = Reminder(
            task_id=task_uuid,
            user_id=context.user_id,
            trigger_at=trigger_at,
            status=ReminderStatus.PENDING.value,
        )
        context.session.add(reminder)
        await context.session.commit()
        await context.session.refresh(reminder)

        return {
            "id": str(reminder.id),
            "task_id": str(reminder.task_id),
            "trigger_at": reminder.trigger_at.isoformat(),
            "status": reminder.status,
        }

    except Exception as e:
        await context.session.rollback()
        return ToolError.create(ToolError.DATABASE_ERROR, "Failed to create reminder.")


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
                "description": "Creates a new task for the user's todo list. Supports priority, tags, due dates, and recurrence.",
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
                        "priority": {
                            "type": "string",
                            "enum": ["none", "low", "medium", "high", "urgent"],
                            "default": "none",
                            "description": "Task priority level",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Task tags/labels (e.g., ['work', 'meeting'])",
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Due date in YYYY-MM-DD format",
                        },
                        "recurrence_rule": {
                            "type": "string",
                            "description": "Recurrence rule (e.g., 'FREQ=DAILY', 'FREQ=WEEKLY;BYDAY=MO')",
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
                "description": "Lists user's tasks with optional filtering, searching, and sorting",
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
                        "q": {
                            "type": "string",
                            "description": "Keyword search across title and description",
                        },
                        "priority": {
                            "type": "string",
                            "description": "Filter by priority (comma-separated, e.g., 'high,urgent')",
                        },
                        "tag": {
                            "type": "string",
                            "description": "Filter by tag (comma-separated, e.g., 'work,meeting')",
                        },
                        "sort_by": {
                            "type": "string",
                            "enum": ["created_at", "priority", "due_date"],
                            "default": "created_at",
                            "description": "Sort field",
                        },
                        "overdue": {
                            "type": "boolean",
                            "description": "Show only overdue tasks (incomplete + past due date)",
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
                "description": "Updates a task's title, description, priority, tags, or due date",
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
                        "priority": {
                            "type": "string",
                            "enum": ["none", "low", "medium", "high", "urgent"],
                            "description": "New priority level",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "New tags (replaces existing)",
                        },
                        "due_date": {
                            "type": "string",
                            "description": "New due date in YYYY-MM-DD format (or empty to remove)",
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
                "description": "Marks a task as completed. For recurring tasks, also generates the next instance.",
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
        {
            "type": "function",
            "function": {
                "name": "set_reminder",
                "description": "Creates a reminder for a task. Provide either an absolute time or relative offset from due date.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "ID of the task to set reminder for",
                        },
                        "trigger_at": {
                            "type": "string",
                            "description": "Absolute trigger time in ISO format (e.g., '2026-03-14T09:00:00Z')",
                        },
                        "relative_to_due": {
                            "type": "string",
                            "description": "Relative offset from due date (e.g., '-1d' for 1 day before, '-2h' for 2 hours before)",
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
    "set_reminder": set_reminder,
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
