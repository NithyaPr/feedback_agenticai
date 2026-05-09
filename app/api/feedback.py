from fastapi import APIRouter, HTTPException
from app.models.schemas import FeedbackRequest, FeedbackResponse
from app.graph.workflow import run_feedback_workflow
from datetime import datetime

router = APIRouter(prefix="/api", tags=["feedback"])


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    try:
        result = run_feedback_workflow(
            product=request.product,
            feedback_text=request.feedback_text,
            user_id=request.user_id
        )

        if result.get("error"):
            return FeedbackResponse(
                success=False,
                message=result["error"],
                llm_response=None,
                timestamp=datetime.now()
            )

        return FeedbackResponse(
            success=True,
            message="Feedback submitted successfully",
            llm_response=result.get("llm_response"),
            timestamp=datetime.now()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))