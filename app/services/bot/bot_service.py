import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.session import NewsBotSession
from app.schemas.message import MessageCreate, MessageResponse


class BotService:
    """Service for managing news bot interactions."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.sessions_collection = db.bot_sessions
        self.messages_collection = db.bot_messages

    async def create_session(self) -> str:
        """Create a new bot session."""
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "messages": [],
            "context": {},
            "is_active": True,
            "expires_at": datetime.utcnow() + timedelta(hours=24),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        await self.sessions_collection.insert_one(session_data)
        return session_id

    async def get_session(self, session_id: str) -> Optional[NewsBotSession]:
        """Get a bot session by ID."""
        session_data = await self.sessions_collection.find_one(
            {"session_id": session_id}
        )
        if session_data:
            return NewsBotSession(**session_data)
        return None

    async def process_message(self, message: MessageCreate) -> MessageResponse:
        """Process a user message and return bot response."""
        # Placeholder: integrate with AI later
        bot_response = (
            f"I received your message: '{message.content}'. "
            "This is a placeholder response from the NewsBot AI."
        )

        response = MessageResponse(
            id=str(uuid.uuid4()),
            content=bot_response,
            session_id=message.session_id or "default",
            timestamp=datetime.utcnow(),
            sender="bot",
        )
        return response

    async def get_session_messages(self, session_id: str) -> List[MessageResponse]:
        """Get all messages for a session."""
        # Placeholder: retrieve stored messages
        return []

    async def update_session_context(self, session_id: str, context: dict):
        """Update session context."""
        await self.sessions_collection.update_one(
            {"session_id": session_id},
            {"$set": {"context": context, "updated_at": datetime.utcnow()}},
        )
