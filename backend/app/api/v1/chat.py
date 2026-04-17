from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.api.deps import ChatServiceDep, ConversationRepoDep
from app.schemas.chat import ChatRequest

router = APIRouter()


@router.post(
    "/chat",
    summary="Chat with the assistant",
    description="Streams a response using the Vercel AI SDK Data Stream Protocol v4.",
)
async def chat(
    request: ChatRequest,
    svc: ChatServiceDep,
    conv_repo: ConversationRepoDep,
) -> StreamingResponse:
    """Handle a chat turn; stream the response back to the client."""
    conversation_id = request.conversation_id

    if not conversation_id:
        conv = conv_repo.create_conversation()
        conversation_id = conv.id

    user_message = request.messages[-1].content if request.messages else ""

    return StreamingResponse(
        svc.stream(conversation_id=conversation_id, user_message=user_message),
        media_type="text/plain; charset=utf-8",
        headers={"x-vercel-ai-data-stream": "v1"},
    )
