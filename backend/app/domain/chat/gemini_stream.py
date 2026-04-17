import json
import uuid
from collections.abc import AsyncIterator
from typing import Any, cast

from google.genai import types
from google.genai.chats import AsyncChat

from app.core.observability import get_logger
from app.domain.chat.citations import Citation, parse_citations, validate_citations
from app.schemas.rag import ChunkResult
from app.tools.registry import Services, dispatch

logger = get_logger(__name__)

MAX_TOOL_ROUNDS = 5


def aisdk_text(text: str) -> str:
    return f"0:{json.dumps(text)}\n"


def aisdk_tool_call(tool_call_id: str, tool_name: str, args: dict[str, Any]) -> str:
    return f"9:{json.dumps({'toolCallId': tool_call_id, 'toolName': tool_name, 'args': args})}\n"


def aisdk_tool_result(tool_call_id: str, result: str) -> str:
    return f"a:{json.dumps({'toolCallId': tool_call_id, 'result': result})}\n"


def aisdk_data(data: list[dict[str, Any]]) -> str:
    return f"2:{json.dumps(data)}\n"


def aisdk_finish(reason: str = "stop") -> str:
    return f"d:{json.dumps({'finishReason': reason})}\n"


def _citation_to_dict(c: Citation) -> dict[str, str]:
    return {"source": c.source, "section": c.section}


def _parse_chunk_result(cd: dict[str, Any]) -> ChunkResult:
    return ChunkResult(
        text=str(cd.get("text", "")),
        source=str(cd.get("source", "")),
        page=int(cd.get("page", 0)),
        section=str(cd.get("section", "")),
        score=float(cd.get("score", 0.0)),
    )


async def stream_agentic(  # noqa: C901
    chat: AsyncChat,
    user_message: str,
    services: Services,
    retrieved_chunks: list[ChunkResult] | None = None,
) -> AsyncIterator[str]:
    """Run the agentic loop and yield AI SDK Data Stream Protocol v4 lines."""
    if retrieved_chunks is None:
        retrieved_chunks = []

    all_text = ""

    for round_num in range(MAX_TOOL_ROUNDS):
        msg = user_message if round_num == 0 else "continue"
        response = await chat.send_message_stream(msg)  # type: ignore[reportUnknownMemberType]

        round_text = ""
        function_calls: list[types.FunctionCall] = []

        async for chunk in response:  # type: ignore[reportUnknownVariableType]
            parts = chunk.candidates[0].content.parts  # type: ignore[reportOptionalMemberAccess,reportUnknownMemberType]
            for part in parts:  # type: ignore[reportUnknownVariableType]
                text_val = cast(str | None, getattr(part, "text", None))  # type: ignore[reportUnknownArgumentType]
                fc_val = getattr(part, "function_call", None)  # type: ignore[reportUnknownArgumentType]
                if text_val:
                    round_text += text_val
                    yield aisdk_text(text_val)
                elif fc_val is not None:
                    function_calls.append(cast(types.FunctionCall, fc_val))

        all_text += round_text

        if not function_calls:
            break

        function_responses: list[types.Part] = []
        for fc in function_calls:
            tool_call_id = str(uuid.uuid4())[:8]
            fc_name = str(fc.name or "")
            fc_args: dict[str, Any] = dict(fc.args) if fc.args else {}  # type: ignore[reportUnknownArgumentType]
            yield aisdk_tool_call(tool_call_id, fc_name, fc_args)

            result = await dispatch(fc_name, fc_args, services)
            yield aisdk_tool_result(tool_call_id, result)

            if fc_name == "search_documents":
                try:
                    for cd in json.loads(result):
                        if isinstance(cd, dict):
                            retrieved_chunks.append(_parse_chunk_result(cast(dict[str, Any], cd)))
                except (json.JSONDecodeError, TypeError):
                    pass

            function_responses.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        name=fc_name,
                        response={"result": result},
                    )
                )
            )

        await chat.send_message(function_responses)  # type: ignore[reportUnknownMemberType]

    else:
        yield aisdk_text("\n\n[Maximum tool rounds reached]")
        yield aisdk_finish("length")
        return

    parsed = parse_citations(all_text)
    valid, _rejected = validate_citations(parsed, retrieved_chunks)
    if valid:
        yield aisdk_data([_citation_to_dict(c) for c in valid])

    yield aisdk_finish("stop")
