"""
Chat API Router for Phase III AI Chatbot.

Implements the chat endpoints as defined in:
Contract Reference: specs/004-ai-chatbot/contracts/chat-api.yaml

Endpoints:
- POST /{user_id}/chat - Send message to AI chatbot
- GET /{user_id}/conversations - List user's conversations
- GET /{user_id}/conversations/{id} - Get conversation history
- DELETE /{user_id}/conversations/{id} - Delete conversation
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.auth import get_current_user
from backend.database import get_session
from backend.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationListResponse,
    ConversationDetailResponse,
    ConversationSummary,
    MessageResponse,
    ToolCallResponse,
)
from backend.chat.service import ChatService

from sqlmodel.ext.asyncio.session import AsyncSession


router = APIRouter(
    prefix="/api",
    tags=["Chat"],
)


def validate_user_access(path_user_id: str, token_user_id: str) -> None:
    """
    Validate that the path user_id matches the JWT token user_id.

    Args:
        path_user_id: User ID from URL path
        token_user_id: User ID from JWT token

    Raises:
        HTTPException: 403 if user IDs don't match
    """
    if path_user_id != token_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: cannot access other users' resources",
        )


@router.post(
    "/{user_id}/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message to the AI chatbot",
    description="""
    Sends a user message to the AI assistant and returns the response.
    Creates a new conversation if conversation_id is not provided.
    Persists both user message and assistant response to database.
    """,
)
async def send_chat_message(
    user_id: str,
    request: ChatRequest,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user),
) -> ChatResponse:
    """
    Send a chat message and get AI response.

    Args:
        user_id: User ID from URL path
        request: Chat request with message and optional conversation_id
        session: Database session
        current_user_id: User ID from JWT token

    Returns:
        ChatResponse with conversation_id, response, and tool_calls

    Raises:
        HTTPException: 403 if user_id mismatch, 503 if AI service unavailable
    """
    # Validate user access
    validate_user_access(user_id, current_user_id)

    # Initialize chat service
    chat_service = ChatService(session)

    try:
        # Process the message
        result = await chat_service.process_message(
            user_id=user_id,
            message=request.message,
            conversation_id=request.conversation_id,
        )

        return ChatResponse(
            conversation_id=UUID(result["conversation_id"]),
            response=result["response"],
            tool_calls=[
                ToolCallResponse(
                    tool=tc["tool"],
                    parameters=tc["parameters"],
                    result=tc.get("result"),
                    success=tc["success"],
                )
                for tc in result.get("tool_calls", [])
            ],
        )

    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Chat error: {e}")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is temporarily unavailable. Please try again later.",
        )


@router.get(
    "/{user_id}/conversations",
    response_model=ConversationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List user's conversations",
    description="Returns a paginated list of the user's chat conversations, sorted by most recent.",
)
async def list_conversations(
    user_id: str,
    limit: int = Query(default=20, le=100, ge=1),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user),
) -> ConversationListResponse:
    """
    List user's conversations.

    Args:
        user_id: User ID from URL path
        limit: Maximum conversations to return (default 20, max 100)
        offset: Pagination offset
        session: Database session
        current_user_id: User ID from JWT token

    Returns:
        Paginated list of conversation summaries
    """
    # Validate user access
    validate_user_access(user_id, current_user_id)

    # Initialize chat service
    chat_service = ChatService(session)

    # Get conversations
    conversations, total = await chat_service.list_conversations(
        user_id=user_id,
        limit=limit,
        offset=offset,
    )

    return ConversationListResponse(
        conversations=[
            ConversationSummary(
                id=UUID(conv["id"]),
                title=conv.get("title"),
                created_at=datetime.fromisoformat(conv["created_at"]),
                updated_at=datetime.fromisoformat(conv["updated_at"]),
                message_count=conv["message_count"],
            )
            for conv in conversations
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{user_id}/conversations/{conversation_id}",
    response_model=ConversationDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get conversation history",
    description="Returns messages for a specific conversation, paginated.",
)
async def get_conversation(
    user_id: str,
    conversation_id: UUID,
    limit: int = Query(default=50, le=100, ge=1),
    before: Optional[datetime] = Query(default=None),
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user),
) -> ConversationDetailResponse:
    """
    Get conversation with messages.

    Args:
        user_id: User ID from URL path
        conversation_id: Conversation ID
        limit: Maximum messages to return (default 50, max 100)
        before: Get messages before this timestamp (for pagination)
        session: Database session
        current_user_id: User ID from JWT token

    Returns:
        Conversation with messages

    Raises:
        HTTPException: 404 if conversation not found
    """
    # Validate user access
    validate_user_access(user_id, current_user_id)

    # Initialize chat service
    chat_service = ChatService(session)

    # Get conversation
    conversation = await chat_service.get_conversation(
        user_id=user_id,
        conversation_id=conversation_id,
        limit=limit,
        before=before,
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return ConversationDetailResponse(
        id=UUID(conversation["id"]),
        title=conversation.get("title"),
        created_at=datetime.fromisoformat(conversation["created_at"]),
        updated_at=datetime.fromisoformat(conversation["updated_at"]),
        messages=[
            MessageResponse(
                id=UUID(msg["id"]),
                role=msg["role"],
                content=msg["content"],
                created_at=datetime.fromisoformat(msg["created_at"]),
                tool_calls=[
                    ToolCallResponse(
                        tool=tc["tool"],
                        parameters=tc["parameters"],
                        result=tc.get("result"),
                        success=tc["success"],
                    )
                    for tc in msg.get("tool_calls", [])
                ],
            )
            for msg in conversation["messages"]
        ],
        has_more=conversation.get("has_more", False),
    )


@router.delete(
    "/{user_id}/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a conversation",
    description="Permanently deletes a conversation and all its messages.",
)
async def delete_conversation(
    user_id: str,
    conversation_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user),
) -> None:
    """
    Delete a conversation.

    Args:
        user_id: User ID from URL path
        conversation_id: Conversation ID
        session: Database session
        current_user_id: User ID from JWT token

    Raises:
        HTTPException: 404 if conversation not found
    """
    # Validate user access
    validate_user_access(user_id, current_user_id)

    # Initialize chat service
    chat_service = ChatService(session)

    # Delete conversation
    deleted = await chat_service.delete_conversation(
        user_id=user_id,
        conversation_id=conversation_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
