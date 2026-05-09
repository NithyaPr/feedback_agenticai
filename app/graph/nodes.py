from typing import TypedDict
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service


class FeedbackState(TypedDict):
    product: str
    feedback_text: str
    user_id: str | None
    feedback_id: str | None
    llm_response: str | None
    error: str | None


class ChatState(TypedDict):
    message: str
    product_filter: str | None
    relevant_feedbacks: list | None
    llm_response: str | None
    error: str | None


def store_feedback_node(state: FeedbackState) -> FeedbackState:
    try:
        feedback_id = vector_store.add_feedback(
            feedback_text=state["feedback_text"],
            product=state["product"],
            user_id=state.get("user_id")
        )
        state["feedback_id"] = feedback_id
    except Exception as e:
        state["error"] = f"Failed to store feedback: {str(e)}"
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
            n_results=10
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