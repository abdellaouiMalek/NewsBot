from datetime import datetime
from typing import List, Optional

from pydantic import Field

from app.models.base import BaseDocument


class NewsBotSession(BaseDocument):
    """NewsBot session model."""

    session_id: str = Field(..., max_length=100)
    messages: List[dict] = Field(default_factory=list)
    context: dict = Field(default_factory=dict)
    is_active: bool = Field(default=True)
    expires_at: Optional[datetime] = Field(None)
