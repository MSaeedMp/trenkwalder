from dataclasses import dataclass


@dataclass
class Message:
    id: str
    conversation_id: str
    role: str
    content: str
    tool_calls_json: str = "[]"
    tool_results_json: str = "[]"
    citations_json: str = "[]"
    created_at: str = ""
