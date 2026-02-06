"""
Chat Service for Phase III AI Chatbot.

This module implements the business logic for chat operations:
- Conversation creation and management
- Message persistence
- Agent orchestration
- Tool call recording

Contract Reference: specs/004-ai-chatbot/contracts/chat-api.yaml
"""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.models import Conversation, Message, MessageRole, ToolCall
from backend.chat.tools import ToolContext
from backend.chat.agent import run_agent


class ChatService:
    """
    Service layer for chat operations.

    Handles all business logic for the chat API endpoints:
    - Creating and retrieving conversations
    - Storing user and assistant messages
    - Running the AI agent
    - Recording tool calls
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the chat service.

        Args:
            session: Database session for persistence
        """
        self.session = session

    async def get_or_create_conversation(
        self,
        user_id: str,
        conversation_id: UUID | None = None,
    ) -> Conversation:
        """
        Get an existing conversation or create a new one.

        Args:
            user_id: User ID from JWT
            conversation_id: Optional existing conversation ID

        Returns:
            Conversation object
        """
        if conversation_id:
            # Try to find existing conversation
            query = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
            result = await self.session.execute(query)
            conversation = result.scalars().first()

            if conversation:
                return conversation

        # Create new conversation
        conversation = Conversation(
            user_id=user_id,
        )
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)

        return conversation

    async def get_conversation_history(
        self,
        conversation_id: UUID,
        user_id: str,
        limit: int = 50,
        before: datetime | None = None,
    ) -> list[Message]:
        """
        Get messages for a conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID for verification
            limit: Maximum messages to return
            before: Only get messages before this timestamp

        Returns:
            List of messages
        """
        # Verify conversation belongs to user
        conv_query = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        conv_result = await self.session.execute(conv_query)
        if not conv_result.scalars().first():
            return []

        # Build message query
        query = select(Message).where(
            Message.conversation_id == conversation_id
        )

        if before:
            query = query.where(Message.created_at < before)

        query = query.order_by(Message.created_at.desc()).limit(limit)

        result = await self.session.execute(query)
        messages = list(result.scalars().all())

        # Reverse to get chronological order
        messages.reverse()

        return messages

    async def store_message(
        self,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
    ) -> Message:
        """
        Store a message in the database.

        Args:
            conversation_id: Conversation ID
            role: Message role (user/assistant/system)
            content: Message content

        Returns:
            Created message
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)

        # Update conversation timestamp
        conv_query = select(Conversation).where(
            Conversation.id == conversation_id
        )
        conv_result = await self.session.execute(conv_query)
        conversation = conv_result.scalars().first()
        if conversation:
            conversation.update_timestamp()
            self.session.add(conversation)
            await self.session.commit()

        return message

    async def store_tool_calls(
        self,
        message_id: UUID,
        tool_calls: list[dict[str, Any]],
    ) -> list[ToolCall]:
        """
        Store tool calls for a message.

        Args:
            message_id: ID of the assistant message
            tool_calls: List of tool call data

        Returns:
            List of created ToolCall records
        """
        records = []
        for tc in tool_calls:
            tool_call = ToolCall(
                message_id=message_id,
                tool_name=tc.get("tool", "unknown"),
                parameters=tc.get("parameters", {}),
                result=tc.get("result"),
                success=tc.get("success", False),
                error_message=tc.get("error_message"),
            )
            self.session.add(tool_call)
            records.append(tool_call)

        await self.session.commit()

        # Refresh all records
        for record in records:
            await self.session.refresh(record)

        return records

    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_id: UUID | None = None,
    ) -> dict[str, Any]:
        """
        Process a user message and generate a response.

        This is the main entry point for chat operations:
        1. Get or create conversation
        2. Load conversation history
        3. Store user message
        4. Run AI agent
        5. Store assistant response and tool calls
        6. Return response

        Args:
            user_id: User ID from JWT
            message: User's message
            conversation_id: Optional existing conversation ID

        Returns:
            Response dict with conversation_id, response, and tool_calls
        """
        # Get or create conversation
        conversation = await self.get_or_create_conversation(
            user_id, conversation_id
        )

        # Load conversation history
        history = await self.get_conversation_history(
            conversation.id, user_id, limit=20
        )

        # Store user message
        user_message = await self.store_message(
            conversation.id,
            MessageRole.USER,
            message,
        )

        # Create tool context
        context = ToolContext(
            user_id=user_id,
            session=self.session,
            conversation_id=conversation.id,
        )

        # Run agent
        try:
            response_text, tool_calls = await run_agent(
                message, history, context
            )
        except Exception as e:
            # Handle agent errors gracefully
            response_text = "I'm sorry, but I encountered an error processing your request. Please try again."
            tool_calls = []

        # Store assistant response
        assistant_message = await self.store_message(
            conversation.id,
            MessageRole.ASSISTANT,
            response_text,
        )

        # Store tool calls if any
        if tool_calls:
            await self.store_tool_calls(assistant_message.id, tool_calls)

        # Update conversation title if this is the first message
        if not conversation.title:
            # Use first 50 chars of first user message as title
            conversation.title = message[:50] + ("..." if len(message) > 50 else "")
            self.session.add(conversation)
            await self.session.commit()

        return {
            "conversation_id": str(conversation.id),
            "response": response_text,
            "tool_calls": [
                {
                    "tool": tc.get("tool"),
                    "parameters": tc.get("parameters"),
                    "result": tc.get("result"),
                    "success": tc.get("success", False),
                }
                for tc in tool_calls
            ],
        }

    async def list_conversations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        List user's conversations.

        Args:
            user_id: User ID from JWT
            limit: Maximum conversations to return
            offset: Pagination offset

        Returns:
            Tuple of (conversation list, total count)
        """
        # Get total count
        count_query = select(Conversation).where(
            Conversation.user_id == user_id
        )
        count_result = await self.session.execute(count_query)
        total = len(list(count_result.scalars().all()))

        # Get paginated conversations
        query = select(Conversation).where(
            Conversation.user_id == user_id
        ).order_by(
            Conversation.updated_at.desc()
        ).offset(offset).limit(limit)

        result = await self.session.execute(query)
        conversations = list(result.scalars().all())

        # Get message counts for each conversation
        conversation_list = []
        for conv in conversations:
            msg_query = select(Message).where(
                Message.conversation_id == conv.id
            )
            msg_result = await self.session.execute(msg_query)
            message_count = len(list(msg_result.scalars().all()))

            conversation_list.append({
                "id": str(conv.id),
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "message_count": message_count,
            })

        return conversation_list, total

    async def get_conversation(
        self,
        user_id: str,
        conversation_id: UUID,
        limit: int = 50,
        before: datetime | None = None,
    ) -> dict[str, Any] | None:
        """
        Get a conversation with its messages.

        Args:
            user_id: User ID from JWT
            conversation_id: Conversation ID
            limit: Maximum messages to return
            before: Only get messages before this timestamp

        Returns:
            Conversation dict with messages or None if not found
        """
        # Get conversation
        query = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        result = await self.session.execute(query)
        conversation = result.scalars().first()

        if not conversation:
            return None

        # Get messages
        messages = await self.get_conversation_history(
            conversation_id, user_id, limit, before
        )

        # Get tool calls for each message
        message_list = []
        for msg in messages:
            message_data = {
                "id": str(msg.id),
                "role": msg.role.value if isinstance(msg.role, MessageRole) else msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
                "tool_calls": [],
            }

            # Get tool calls for assistant messages
            if msg.role == MessageRole.ASSISTANT:
                tc_query = select(ToolCall).where(
                    ToolCall.message_id == msg.id
                )
                tc_result = await self.session.execute(tc_query)
                tool_calls = list(tc_result.scalars().all())

                message_data["tool_calls"] = [
                    {
                        "tool": tc.tool_name,
                        "parameters": tc.parameters,
                        "result": tc.result,
                        "success": tc.success,
                    }
                    for tc in tool_calls
                ]

            message_list.append(message_data)

        # Check if there are more messages
        if before is None and len(messages) == limit:
            # Check if there are older messages
            oldest_time = messages[0].created_at if messages else None
            if oldest_time:
                older_query = select(Message).where(
                    Message.conversation_id == conversation_id,
                    Message.created_at < oldest_time,
                ).limit(1)
                older_result = await self.session.execute(older_query)
                has_more = older_result.scalars().first() is not None
            else:
                has_more = False
        else:
            has_more = len(messages) == limit

        return {
            "id": str(conversation.id),
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "messages": message_list,
            "has_more": has_more,
        }

    async def delete_conversation(
        self,
        user_id: str,
        conversation_id: UUID,
    ) -> bool:
        """
        Delete a conversation and all its messages.

        Args:
            user_id: User ID from JWT
            conversation_id: Conversation ID

        Returns:
            True if deleted, False if not found
        """
        # Get conversation
        query = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        result = await self.session.execute(query)
        conversation = result.scalars().first()

        if not conversation:
            return False

        # Delete all tool calls for this conversation's messages
        msg_query = select(Message).where(
            Message.conversation_id == conversation_id
        )
        msg_result = await self.session.execute(msg_query)
        messages = list(msg_result.scalars().all())

        for msg in messages:
            tc_query = select(ToolCall).where(
                ToolCall.message_id == msg.id
            )
            tc_result = await self.session.execute(tc_query)
            tool_calls = list(tc_result.scalars().all())

            for tc in tool_calls:
                await self.session.delete(tc)

            await self.session.delete(msg)

        # Delete conversation
        await self.session.delete(conversation)
        await self.session.commit()

        return True
