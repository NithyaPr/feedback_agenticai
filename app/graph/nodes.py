from typing import TypedDict, List, Optional
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service


class FeedbackState(TypedDict):
    product: str
    feedback_text: str
    nps_score: int
    user_id: Optional[str]
    feedback_id: Optional[str]
    categories: List[str]
    llm_response: Optional[str]
    error: Optional[str]


class ChatState(TypedDict):
    message: str
    product_filter: Optional[str]
    min_nps: Optional[int]
    max_nps: Optional[int]
    categories_filter: Optional[List[str]]
    relevant_feedbacks: Optional[List]
    llm_response: Optional[str]
    error: Optional[str]


def store_feedback_node(state: FeedbackState) -> FeedbackState:
    try:
        feedback_id = vector_store.add_feedback(
            feedback_text=state["feedback_text"],
            product=state["product"],
            nps_score=state["nps_score"],
            user_id=state.get("user_id"),
            categories=[]
        )
        state["feedback_id"] = feedback_id
        state["categories"] = []
    except Exception as e:
        state["error"] = f"Failed to store feedback: {str(e)}"
    return state


def categorize_feedback_node(state: FeedbackState) -> FeedbackState:
    if state.get("error"):
        return state

    try:
        categories = llm_service.categorize_feedback(state["feedback_text"])
        state["categories"] = categories

        if state.get("feedback_id"):
            vector_store.update_feedback_categories(
                state["feedback_id"],
                categories
            )
    except Exception as e:
        state["error"] = f"Failed to categorize feedback: {str(e)}"
    return state


def generate_feedback_response_node(state: FeedbackState) -> FeedbackState:
    if state.get("error"):
        return state

    try:
        llm_response = llm_service.generate_feedback_response(
            feedback_text=state["feedback_text"],
            product=state["product"]
        )
        state["llm_response"] = llm_response
    except Exception as e:
        state["error"] = f"Failed to generate response: {str(e)}"
    return state


def retrieve_feedbacks_node(state: ChatState) -> ChatState:
    try:
        relevant_feedbacks = vector_store.query(
            query_text=state["message"],
            product_filter=state.get("product_filter"),
            n_results=10,
            min_nps=state.get("min_nps"),
            max_nps=state.get("max_nps"),
            categories=state.get("categories_filter")
        )
        state["relevant_feedbacks"] = relevant_feedbacks
    except Exception as e:
        state["error"] = f"Failed to retrieve feedbacks: {str(e)}"
    return state


def generate_chat_response_node(state: ChatState) -> ChatState:
    if state.get("error"):
        return state

    try:
        llm_response = llm_service.generate_chat_response(
            user_message=state["message"],
            relevant_feedbacks=state.get("relevant_feedbacks", []),
            product_filter=state.get("product_filter")
        )
        state["llm_response"] = llm_response
    except Exception as e:
        state["error"] = f"Failed to generate chat response: {str(e)}"
    return state