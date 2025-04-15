from logging import getLogger
from typing import Optional

from core import storage
from core.authentication.auth_middleware import get_current_token
from core.mcp_client import MCPClient, get_mcp_client
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from schemas.base import ValidIdStr
from schemas.conversation import ChatInput, ChatResponse, Conversation
from schemas.page import Page
from schemas.token import TokenData

router = APIRouter()


@router.get(path="/conversations", response_model=Page[Conversation])
def get_conversations(
    cursor: Optional[str] = None,
    limit: int = Query(default=10, ge=1, le=100),
    current_token: TokenData = Depends(get_current_token),
) -> Page[Conversation]:
    """Gets a page of conversations for a user"""
    logger = getLogger(__name__ + ".get_conversations")
    try:
        conversations = storage.conversations.get_page(
            {"user_id": current_token.id}, limit=limit, cursor=cursor
        )

        return conversations
    except HTTPException as ex:
        logger.exception(ex)
        raise ex
    except Exception as ex:
        logger.exception(ex)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to get conversations",
        )


@router.get(path="/conversations/{conversation_id}", response_model=Conversation)
def get_conversation(
    conversation_id: ValidIdStr,
    current_token: TokenData = Depends(get_current_token),
) -> Conversation:
    """Gets a conversations for a user"""
    logger = getLogger(__name__ + ".get_conversation")
    try:
        conversation = storage.conversations.verify(
            {"_id": conversation_id, "user_id": current_token.id}
        )

        return conversation
    except HTTPException as ex:
        logger.exception(ex)
        raise ex
    except Exception as ex:
        logger.exception(ex)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to get conversation",
        )


@router.post(path="/conversations", response_model=Conversation)
def create_conversation(
    title: Optional[str] = Body(default=None, embed=True),
    current_token: TokenData = Depends(get_current_token),
) -> Conversation:
    """Creates a new conversation"""
    logger = getLogger(__name__ + ".create_conversation")
    try:
        data = {"user_id": current_token.id, "title": title, "history": []}

        id = storage.conversations.create(data)

        conversation = storage.conversations.verify(
            {"_id": id, "user_id": current_token.id}
        )
        return conversation
    except HTTPException as ex:
        logger.exception(ex)
        raise ex
    except Exception as ex:
        logger.exception(ex)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create conversation",
        )


@router.post(path="/conversations/{conversation_id}", response_model=ChatResponse)
async def chat(
    conversation_id: ValidIdStr,
    input: ChatInput,
    current_token: TokenData = Depends(get_current_token),
    agent: MCPClient = Depends(get_mcp_client),
) -> ChatResponse:
    """Sends a prompt in a conversation and returns the agent's response"""
    logger = getLogger(__name__ + ".chat")
    try:
        conversation = storage.conversations.verify(
            {"_id": conversation_id, "user_id": current_token.id}
        )

        new_messages = [{"role": "user", "content": input.prompt}]
        history = [item.model_dump() for item in conversation.history] + new_messages

        agent.mcp_server_addresses = input.tools

        response = await agent.run(history)
        new_messages.append({"role": "assistant", "content": response})

        storage.conversations.advanced_update(
            filter={"_id": conversation_id, "user_id": current_token.id},
            update={"$push": {"history": {"$each": new_messages}}},
        )

        return ChatResponse(message=response)

    except HTTPException as ex:
        logger.exception(ex)
        raise ex
    except Exception as ex:
        logger.exception(ex)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process message",
        )
