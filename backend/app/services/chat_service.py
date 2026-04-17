import contextlib
import json
from collections.abc import AsyncIterator
from typing import Any

from google import genai
from google.genai import types

from app.core.observability import get_logger
from app.domain.chat.citations import parse_citations, validate_citations
from app.domain.chat.gemini_stream import stream_agentic
from app.domain.chat.system_prompt import SYSTEM_PROMPT
from app.models import Message
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.rag import ChunkResult
from app.tools.registry import Services, dispatch

logger = get_logger(__name__)


class ChatService:
    """Drives the Gemini agentic loop and yields AI SDK stream lines."""

    def __init__(
        self,
        client: genai.Client,
        services: Services,
        tool_declarations: list[types.FunctionDeclaration],
        conversation_repo: ConversationRepository,
        model: str = "gemini-2.5-flash",
    ) -> None:
        self._client = client
        self._services = services
        self._tool_declarations = tool_declarations
        self._conversation_repo = conversation_repo
        self._model = model

    def _messages_to_history(self, messages: list[Message]) -> list[Any]:
        history: list[Any] = []
        for msg in messages:
            role = "model" if msg.role == "assistant" else "user"
            history.append(types.Content(role=role, parts=[types.Part(text=msg.content)]))
        return history

    async def stream(
        self,
        conversation_id: str,
        user_message: str,
    ) -> AsyncIterator[bytes]:
        """Load history, run agentic loop, save results, yield UTF-8 AI SDK lines."""
        history_messages = self._conversation_repo.get_messages(conversation_id)
        history = self._messages_to_history(history_messages)

        self._conversation_repo.add_message(
            conversation_id=conversation_id,
            role="user",
            content=user_message,
        )

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[types.Tool(function_declarations=self._tool_declarations)],
        )

        chat = self._client.aio.chats.create(  # type: ignore[reportUnknownMemberType,reportArgumentType]
            model=self._model,
            config=config,
            history=history,
        )

        logger.info("chat_stream_started", conversation_id=conversation_id, model=self._model)

        full_response = ""
        collected_tool_calls: list[dict[str, object]] = []
        collected_tool_results: list[dict[str, object]] = []
        retrieved_chunks: list[ChunkResult] = []

        async def execute_tool(name: str, args: dict[str, Any]) -> str:
            return await dispatch(name, args, self._services)

        async for line in stream_agentic(
            chat=chat,
            user_message=user_message,
            execute_tool=execute_tool,
            retrieved_chunks=retrieved_chunks,
        ):
            yield line.encode("utf-8")

            if line.startswith("0:"):
                with contextlib.suppress(json.JSONDecodeError, TypeError):
                    full_response += json.loads(line[2:])
            elif line.startswith("9:"):
                with contextlib.suppress(json.JSONDecodeError, TypeError):
                    collected_tool_calls.append(json.loads(line[2:]))
            elif line.startswith("a:"):
                with contextlib.suppress(json.JSONDecodeError, TypeError):
                    collected_tool_results.append(json.loads(line[2:]))

        parsed = parse_citations(full_response)
        valid, _rejected = validate_citations(parsed, retrieved_chunks)
        citation_dicts = [{"source": c.source, "section": c.section} for c in valid]

        self._conversation_repo.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=full_response,
            tool_calls=collected_tool_calls,
            tool_results=collected_tool_results,
            citations=citation_dicts,
        )

        logger.info(
            "chat_stream_completed",
            conversation_id=conversation_id,
            response_len=len(full_response),
            tool_calls=len(collected_tool_calls),
            citations=len(citation_dicts),
        )
