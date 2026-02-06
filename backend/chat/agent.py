"""
OpenAI Agent Configuration for Phase III AI Chatbot.

This module configures the stateless AI agent with tool bindings:
- Initializes OpenAI client with environment API key
- Defines agent system instructions
- Registers MCP tools as OpenAI functions
- Implements run_agent() for conversation handling

Contract Reference: specs/004-ai-chatbot/plan.md Phase 4
"""

import json
from typing import Any
from uuid import UUID

from openai import OpenAI

from backend.chat.tools import (
    ToolContext,
    execute_tool,
    get_tool_definitions,
)
from backend.config import settings
from backend.models import Message, MessageRole, ToolCall


# System instructions for the AI agent
SYSTEM_INSTRUCTIONS = """You are a helpful AI assistant for a Todo application. Your role is to help users manage their tasks through natural conversation.

## Your Capabilities
You can help users:
- Add new tasks to their list
- View their current tasks (all, pending, or completed)
- Update task titles or descriptions
- Mark tasks as complete or incomplete
- Delete tasks they no longer need

## Behavior Guidelines

### Confirmation Before Actions
- Always confirm what you're about to do before executing destructive actions (delete)
- For task creation, you can proceed directly but confirm the action was successful
- When listing tasks, present them in a clear, readable format

### Clarification
- If a user's request is ambiguous, ask for clarification before acting
- Examples of ambiguous requests:
  - "Delete that task" (which one?)
  - "Mark it done" (which task?)
  - "Add groceries" (is this a task title or a request for clarification?)

### Response Style
- Be conversational and friendly, but concise
- Use natural language to confirm actions (e.g., "I've added 'Buy groceries' to your list!")
- When showing task lists, format them clearly
- If an operation fails, explain what went wrong in user-friendly terms

### Security
- You can only access and modify tasks belonging to the current user
- Never expose internal system details, error codes, or technical implementation
- If something fails, provide a helpful message without revealing internals

### Task Reference
When users refer to tasks by name (e.g., "mark buy groceries as done"), try to match the task by title. If multiple tasks match or no tasks match, ask for clarification.
"""


def get_openai_client() -> OpenAI:
    """
    Initialize OpenAI client with API key from settings.

    Returns:
        Configured OpenAI client
    """
    return OpenAI(api_key=settings.openai_api_key)


def format_messages_for_openai(
    messages: list[Message],
    current_message: str,
) -> list[dict[str, Any]]:
    """
    Format conversation history for OpenAI API.

    Args:
        messages: Previous messages in the conversation
        current_message: The new user message

    Returns:
        Formatted messages list for OpenAI
    """
    formatted = [{"role": "system", "content": SYSTEM_INSTRUCTIONS}]

    # Add conversation history
    for msg in messages:
        role = msg.role.value if isinstance(msg.role, MessageRole) else msg.role
        if role in ["user", "assistant"]:
            formatted.append({
                "role": role,
                "content": msg.content,
            })

    # Add current message
    formatted.append({
        "role": "user",
        "content": current_message,
    })

    return formatted


async def run_agent(
    message: str,
    history: list[Message],
    context: ToolContext,
) -> tuple[str, list[dict[str, Any]]]:
    """
    Run the AI agent with a user message.

    This function:
    1. Formats the conversation history
    2. Calls OpenAI with tool definitions
    3. Executes any tool calls
    4. Returns the final response

    Args:
        message: User's message
        history: Previous messages in the conversation
        context: Execution context with user_id and session

    Returns:
        Tuple of (response_text, tool_calls_list)
    """
    client = get_openai_client()
    tools = get_tool_definitions()

    # Format messages for OpenAI
    messages = format_messages_for_openai(history, message)

    tool_calls_results: list[dict[str, Any]] = []

    # Make initial API call
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    assistant_message = response.choices[0].message

    # Process tool calls if any
    while assistant_message.tool_calls:
        # Add assistant message to conversation
        messages.append({
            "role": "assistant",
            "content": assistant_message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in assistant_message.tool_calls
            ],
        })

        # Execute each tool call
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            try:
                params = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                params = {}

            # Execute the tool
            result = await execute_tool(tool_name, params, context)

            # Track tool call for response
            tool_call_info = {
                "tool": tool_name,
                "parameters": params,
                "result": result if not result.get("error") else None,
                "success": not result.get("error", False),
            }
            if result.get("error"):
                tool_call_info["error_message"] = result.get("message")

            tool_calls_results.append(tool_call_info)

            # Add tool result to conversation
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            })

        # Get next response from OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message

    # Return final response
    return assistant_message.content or "", tool_calls_results


async def get_agent_response(
    message: str,
    history: list[Message],
    context: ToolContext,
) -> dict[str, Any]:
    """
    High-level wrapper for agent execution.

    Args:
        message: User's message
        history: Conversation history
        context: Execution context

    Returns:
        Response dict with text and tool calls
    """
    try:
        response_text, tool_calls = await run_agent(message, history, context)

        return {
            "response": response_text,
            "tool_calls": tool_calls,
            "success": True,
        }
    except ValueError as e:
        # API key not set
        return {
            "response": "I'm sorry, but I'm unable to process your request right now. Please try again later.",
            "tool_calls": [],
            "success": False,
            "error": str(e),
        }
    except Exception as e:
        # Other errors
        return {
            "response": "I encountered an error while processing your request. Please try again.",
            "tool_calls": [],
            "success": False,
            "error": str(e),
        }
