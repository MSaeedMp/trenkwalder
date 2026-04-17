import json
import tempfile

import lancedb
import pytest

from app.repositories import ConversationRepository


@pytest.fixture
def repo() -> ConversationRepository:
    tmpdir = tempfile.mkdtemp()
    db = lancedb.connect(tmpdir)
    return ConversationRepository(db)


@pytest.mark.integration
def test_create_conversation(repo: ConversationRepository) -> None:
    conv = repo.create_conversation(user_id="me")
    assert conv.id
    assert conv.user_id == "me"


@pytest.mark.integration
def test_get_conversation(repo: ConversationRepository) -> None:
    conv = repo.create_conversation()
    found = repo.get_conversation(conv.id)
    assert found is not None
    assert found.id == conv.id


@pytest.mark.integration
def test_get_missing_conversation(repo: ConversationRepository) -> None:
    assert repo.get_conversation("nonexistent") is None


@pytest.mark.integration
def test_add_and_get_messages(repo: ConversationRepository) -> None:
    conv = repo.create_conversation()

    repo.add_message(conv.id, role="user", content="Hello")
    repo.add_message(conv.id, role="assistant", content="Hi there!")

    messages = repo.get_messages(conv.id)
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[0].content == "Hello"
    assert messages[1].role == "assistant"
    assert messages[1].content == "Hi there!"


@pytest.mark.integration
def test_message_with_tool_calls(repo: ConversationRepository) -> None:
    conv = repo.create_conversation()

    msg = repo.add_message(
        conv.id,
        role="assistant",
        content="You have 18 vacation days left.",
        tool_calls=[{"toolName": "get_vacation_balance", "args": {"employee_id": "me"}}],
        tool_results=[{"result": '{"remaining_days": 18}'}],
        citations=[{"source": "benefits.md", "section": "Paid Leave"}],
    )

    assert json.loads(msg.tool_calls_json) == [
        {"toolName": "get_vacation_balance", "args": {"employee_id": "me"}}
    ]
    assert json.loads(msg.citations_json) == [{"source": "benefits.md", "section": "Paid Leave"}]
    assert msg.created_at != ""


@pytest.mark.integration
def test_list_conversations(repo: ConversationRepository) -> None:
    repo.create_conversation(user_id="me")
    repo.create_conversation(user_id="me")
    repo.create_conversation(user_id="other")

    mine = repo.list_conversations(user_id="me")
    assert len(mine) == 2


@pytest.mark.integration
def test_get_messages_empty_conversation(repo: ConversationRepository) -> None:
    conv = repo.create_conversation()
    messages = repo.get_messages(conv.id)
    assert messages == []


@pytest.mark.integration
def test_messages_persist_across_reads(repo: ConversationRepository) -> None:
    conv = repo.create_conversation()
    repo.add_message(conv.id, role="user", content="test")

    messages = repo.get_messages(conv.id)
    assert len(messages) == 1
    assert messages[0].content == "test"
