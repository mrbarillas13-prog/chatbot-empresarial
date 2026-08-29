from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    action: Optional[str] = None
    context: Optional[dict] = None


class ConversationMessage(BaseModel):
    id: UUID
    session_id: str
    role: str
    content: str
    metadata_: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}
