from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    """Schema for creating a message."""

    content: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None)


class MessageResponse(BaseModel):
    """Schema for message response."""

    id: str
    content: str
    session_id: str
    timestamp: datetime
    sender: str  # 'user' or 'bot'

    class Config:
        from_attributes = True
