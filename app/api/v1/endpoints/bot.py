from typing import List

from fastapi import APIRouter, Depends

from app.core.database import get_database
from app.schemas.message import MessageCreate, MessageResponse
from app.services.bot.bot_service import BotService

router = APIRouter()


@router.post("/bot/message", response_model=MessageResponse)
async def send_message(message: MessageCreate, db=Depends(get_database)):
    """Send a message to the news bot."""
    bot_service = BotService(db)
    response = await bot_service.process_message(message)
    return response


@router.get("/bot/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(session_id: str, db=Depends(get_database)):
    """Get all messages for a specific session."""
    bot_service = BotService(db)
    messages = await bot_service.get_session_messages(session_id)
    return messages
