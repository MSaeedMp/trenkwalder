from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.api.deps import ChatServiceDep, ConversationRepoDep
from app.schemas.chat import ChatRequest
from app.schemas.error import ErrorResponse

router = APIRouter()


@router.post(
    "/chat",
    summary="Chat with the assistant",
    description="Streams a response using the Vercel AI SDK Data Stream Protocol v4.",
    tags=["chat"],
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "Streamed chat response (text/event-stream)",
            "content": {"text/event-stream": {}},
        },
        422: {
            "description": "Validation error — invalid request body",
            "model": ErrorResponse,
        },
        503: {
            "description": "Service unavailable — MCP server or LLM unreachable",
            "model": ErrorResponse,
        },
    },
)
async def chat(
    request: ChatRequest,
    svc: ChatServiceDep,
    conv_repo: ConversationRepoDep,
) -> StreamingResponse:
    return StreamingResponse(
        svc.stream(
            conversation_id=request.conversation_id or conv_repo.create_conversation().id,
            user_message=request.messages[-1].content if request.messages else "",
        ),
        media_type="text/event-stream",
        headers={
            "x-vercel-ai-data-stream": "v1",
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
