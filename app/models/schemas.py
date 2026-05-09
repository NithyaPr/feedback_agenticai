from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FeedbackRequest(BaseModel):
    product: str = Field(..., description="Product name")
    feedback_text: str = Field(..., description="User's feedback")
    user_id: Optional[str] = Field(None, description="Optional user identifier")


class FeedbackResponse(BaseModel):
    success: bool
    message: str
    llm_response: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    message: str = Field(..., description="Product manager's question")
    product_filter: Optional[str] = Field(None, description="Filter by product name")


class ChatResponse(BaseModel):
    success: bool
    response: str
    relevant_feedbacks: Optional[list] = None
    timestamp: datetime = Field(default_factory=datetime.now)