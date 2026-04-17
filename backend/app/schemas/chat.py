from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    conversation_id: str | None = None
    messages: list["ChatMessage"]


class ChatMessage(BaseModel):
    role: str = Field(..., description="user or assistant")
    content: str
