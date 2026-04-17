from typing import Annotated

from fastapi import Depends, Request

from app.repositories.conversation_repository import ConversationRepository
from app.services.chat_service import ChatService


def get_chat_service(request: Request) -> ChatService:
    return request.app.state.chat_service  # type: ignore[no-any-return]


def get_conversation_repo(request: Request) -> ConversationRepository:
    return request.app.state.conversation_repo  # type: ignore[no-any-return]


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
ConversationRepoDep = Annotated[ConversationRepository, Depends(get_conversation_repo)]
