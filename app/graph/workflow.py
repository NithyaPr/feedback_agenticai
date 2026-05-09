from langgraph.graph import StateGraph, END
from app.graph.nodes import (
    FeedbackState,
    ChatState,
    store_feedback_node,
    generate_feedback_response_node,
    retrieve_feedbacks_node,
    generate_chat_response_node
)


def create_feedback_graph():
    workflow = StateGraph(FeedbackState)

    workflow.add_node("store_feedback", store_feedback_node)
    workflow.add_node("generate_response", generate_feedback_response_node)

    workflow.set_entry_point("store_feedback")
    workflow.add_edge("store_feedback", "generate_response")
    workflow.add_edge("generate_response", END)

    return workflow.compile()


def create_chat_graph():
    workflow = StateGraph(ChatState)

    workflow.add_node("retrieve_feedbacks", retrieve_feedbacks_node)
    workflow.add_node("generate_chat_response", generate_chat_response_node)

    workflow.set_entry_point("retrieve_feedbacks")
    workflow.add_edge("retrieve_feedbacks", "generate_chat_response")
    workflow.add_edge("generate_chat_response", END)

    return workflow.compile()


feedback_graph = create_feedback_graph()
chat_graph = create_chat_graph()


def run_feedback_workflow(product: str, feedback_text: str, user_id: str = None) -> dict:
    initial_state: FeedbackState = {
        "product": product,
        "feedback_text": feedback_text,
        "user_id": user_id,
        "feedback_id": None,
        "llm_response": None,
        "error": None
    }

    result = feedback_graph.invoke(initial_state)
    return result


def run_chat_workflow(message: str, product_filter: str = None) -> dict:
    initial_state: ChatState = {
        "message": message,
        "product_filter": product_filter,
        "relevant_feedbacks": None,
        "llm_response": None,
        "error": None
    }

    result = chat_graph.invoke(initial_state)
    return result