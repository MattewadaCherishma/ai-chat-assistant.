from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

Tone = Literal["professional", "casual", "concise"]

class CreateConversationResponse(BaseModel):
    conversation_id: str
    created_at: datetime

class SendMessageRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=12000)
    tone: Tone = "professional"

class RegenerateRequest(BaseModel):
    tone: Tone = "professional"

class MessageResponse(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime
    tone: Tone | None = None

class ConversationSummary(BaseModel):
    conversation_id: str
    title: str
    created_at: datetime
    updated_at: datetime

class ConversationDetail(ConversationSummary):
    messages: list[MessageResponse]
