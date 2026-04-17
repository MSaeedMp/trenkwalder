import json

import pytest

from app.domain.chat.gemini_stream import (
    aisdk_data,
    aisdk_finish,
    aisdk_text,
    aisdk_tool_call,
    aisdk_tool_result,
)


@pytest.mark.contract
def test_text_line_format() -> None:
    line = aisdk_text("hello world")
    assert line.startswith("0:")
    assert line.endswith("\n")
    payload = json.loads(line[2:])
    assert payload == "hello world"


@pytest.mark.contract
def test_tool_call_line_format() -> None:
    line = aisdk_tool_call("abc123", "search_documents", {"query": "test"})
    assert line.startswith("9:")
    assert line.endswith("\n")
    payload = json.loads(line[2:])
    assert payload["toolCallId"] == "abc123"
    assert payload["toolName"] == "search_documents"
    assert payload["args"]["query"] == "test"


@pytest.mark.contract
def test_tool_result_line_format() -> None:
    line = aisdk_tool_result("abc123", '{"text": "found"}')
    assert line.startswith("a:")
    assert line.endswith("\n")
    payload = json.loads(line[2:])
    assert payload["toolCallId"] == "abc123"
    assert payload["result"] == '{"text": "found"}'


@pytest.mark.contract
def test_data_line_format() -> None:
    citations = [{"source": "doc.md", "section": "Intro"}]
    line = aisdk_data(citations)
    assert line.startswith("2:")
    assert line.endswith("\n")
    payload = json.loads(line[2:])
    assert payload[0]["source"] == "doc.md"


@pytest.mark.contract
def test_finish_line_format_stop() -> None:
    line = aisdk_finish("stop")
    assert line.startswith("d:")
    assert line.endswith("\n")
    payload = json.loads(line[2:])
    assert payload["finishReason"] == "stop"


@pytest.mark.contract
def test_finish_line_format_length() -> None:
    line = aisdk_finish("length")
    payload = json.loads(line[2:])
    assert payload["finishReason"] == "length"
