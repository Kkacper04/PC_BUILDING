from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"] = Field(..., description="Message role")
    content: str = Field(..., min_length=1, max_length=4000)

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., min_length=1)

class ChatResponse(BaseModel):
    message: str
    suggested_build: Optional[Dict[str, Optional[int]]] = None
