"""
Phase III: AI Chatbot Module

This module provides AI-powered chat functionality for the Todo application.
It includes:
- OpenAI agent configuration
- MCP tool implementations for task operations
- Chat service for conversation management
"""

from backend.chat.tools import (
    ToolContext,
    add_task,
    list_tasks,
    update_task,
    complete_task,
    delete_task,
    get_tool_definitions,
)
from backend.chat.agent import run_agent
from backend.chat.service import ChatService

__all__ = [
    "ToolContext",
    "add_task",
    "list_tasks",
    "update_task",
    "complete_task",
    "delete_task",
    "get_tool_definitions",
    "run_agent",
    "ChatService",
]
