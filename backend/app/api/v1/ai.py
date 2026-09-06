from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.api.schemas.ai_schemas import ChatRequest, ChatResponse
from app.logic.ai_agent import process_chat

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest, db: Session = Depends(get_db)):
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    result = await process_chat(db, messages)
    
    return ChatResponse(
        message=result["message"],
        suggested_build=result["suggested_build"]
    )
