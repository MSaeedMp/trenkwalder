import json
import uuid
from dataclasses import asdict
from datetime import UTC, datetime
from typing import Any, cast

import lancedb

from app.core.observability import get_logger
from app.models import Conversation, Message

logger = get_logger(__name__)

CONVERSATIONS_TABLE = "conversations"
MESSAGES_TABLE = "messages"


def _row_to_conversation(row: dict[str, Any]) -> Conversation:
    return Conversation(
        id=str(row.get("id", "")),
        user_id=str(row.get("user_id", "me")),
        title=str(row.get("title", "")),
        created_at=str(row.get("created_at", "")),
    )


def _row_to_message(row: dict[str, Any]) -> Message:
    return Message(
        id=str(row.get("id", "")),
        conversation_id=str(row.get("conversation_id", "")),
        role=str(row.get("role", "")),
        content=str(row.get("content", "")),
        tool_calls_json=str(row.get("tool_calls_json", "[]")),
        tool_results_json=str(row.get("tool_results_json", "[]")),
        citations_json=str(row.get("citations_json", "[]")),
        created_at=str(row.get("created_at", "")),
    )


class ConversationRepository:
    """LanceDB-backed conversation and message store."""

    def __init__(self, db: lancedb.DBConnection) -> None:
        self._db = db

    def _has_table(self, name: str) -> bool:
        return name in self._db.list_tables().tables

    def create_conversation(self, user_id: str = "me") -> Conversation:
        conv = Conversation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            created_at=datetime.now(UTC).isoformat(),
        )
        record = asdict(conv)
        if self._has_table(CONVERSATIONS_TABLE):
            self._db.open_table(CONVERSATIONS_TABLE).add([record])  # type: ignore[reportUnknownMemberType]
        else:
            self._db.create_table(CONVERSATIONS_TABLE, data=[record], mode="overwrite")  # type: ignore[reportUnknownMemberType]
        logger.info("conversation_created", id=conv.id, user_id=user_id)
        return conv

    def get_conversation(self, conversation_id: str) -> Conversation | None:
        if not self._has_table(CONVERSATIONS_TABLE):
            return None
        table = self._db.open_table(CONVERSATIONS_TABLE)
        rows = cast(
            list[dict[str, Any]],
            table.search().where(f"id = '{conversation_id}'").to_list(),  # type: ignore[reportUnknownMemberType]
        )
        if not rows:
            return None
        return _row_to_conversation(rows[0])

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tool_calls: list[dict[str, object]] | None = None,
        tool_results: list[dict[str, object]] | None = None,
        citations: list[dict[str, str]] | None = None,
    ) -> Message:
        msg = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls_json=json.dumps(tool_calls or []),
            tool_results_json=json.dumps(tool_results or []),
            citations_json=json.dumps(citations or []),
            created_at=datetime.now(UTC).isoformat(),
        )
        record = asdict(msg)
        if self._has_table(MESSAGES_TABLE):
            self._db.open_table(MESSAGES_TABLE).add([record])  # type: ignore[reportUnknownMemberType]
        else:
            self._db.create_table(MESSAGES_TABLE, data=[record], mode="overwrite")  # type: ignore[reportUnknownMemberType]
        return msg

    def get_messages(self, conversation_id: str) -> list[Message]:
        if not self._has_table(MESSAGES_TABLE):
            return []
        table = self._db.open_table(MESSAGES_TABLE)
        rows = cast(
            list[dict[str, Any]],
            table.search().where(f"conversation_id = '{conversation_id}'").to_list(),  # type: ignore[reportUnknownMemberType]
        )
        messages = [_row_to_message(r) for r in rows]
        messages.sort(key=lambda m: m.created_at)
        return messages

    def list_conversations(self, user_id: str = "me") -> list[Conversation]:
        if not self._has_table(CONVERSATIONS_TABLE):
            return []
        table = self._db.open_table(CONVERSATIONS_TABLE)
        rows = cast(
            list[dict[str, Any]],
            table.search().where(f"user_id = '{user_id}'").to_list(),  # type: ignore[reportUnknownMemberType]
        )
        return [_row_to_conversation(r) for r in rows]
