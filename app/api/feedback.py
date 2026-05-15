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
            nps_score=request.nps_score,
            user_id=request.user_id
        )

        if result.get("error"):
            return FeedbackResponse(
                success=False,
                message=result["error"],
                llm_response=None,
                nps_score=request.nps_score,
                categories=[],
                timestamp=datetime.now()
            )

        return FeedbackResponse(
            success=True,
            message="Feedback submitted successfully",
            llm_response=result.get("llm_response"),
            nps_score=request.nps_score,
            categories=result.get("categories", []),
            timestamp=datetime.now(),
            is_technical=result.get("is_technical", False),
            duplicate_note=result.get("duplicate_note"),
            intent_note=result.get("intent_note"),
            needs_review=result.get("needs_review", False),
            assigned_team=result.get("assigned_team"),
            kb_references=result.get("kb_references")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))