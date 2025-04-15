from datetime import datetime
from typing import Any, List, Optional

from pydantic import AliasChoices, BaseModel, Field
from schemas.base import PyObjectID


class ChatInput(BaseModel):
    prompt: str
    tools: List[str]


class ChatResponse(BaseModel):
    message: str


class HistoryItem(BaseModel):
    role: str
    content: Any


class Conversation(BaseModel):
    id: PyObjectID = Field(validation_alias=AliasChoices("_id", "id"))
    user_id: str
    title: Optional[str] = None
    history: List[HistoryItem]
    date_created: datetime
    date_modified: datetime
