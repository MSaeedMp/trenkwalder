from dataclasses import dataclass


@dataclass
class Conversation:
    id: str
    user_id: str = "me"
    title: str = ""
    created_at: str = ""
