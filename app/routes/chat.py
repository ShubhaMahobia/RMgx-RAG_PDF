from fastapi import APIRouter
from app.models.chat import ChatMessage

router = APIRouter()

@router.post("/chat/")
async def create_chat_message(chat_message: ChatMessage):
    return {"user": chat_message.user, "message": chat_message.message}
