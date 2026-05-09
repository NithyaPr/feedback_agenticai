from langchain_openai import ChatOpenAI
from config.settings import settings
from typing import Optional, List, Dict, Any


class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7
        )

    def generate_feedback_response(self, feedback_text: str, product: str) -> str:
        prompt = f"""You are a customer support AI. A user has submitted feedback for the product '{product}'.

User's feedback: "{feedback_text}"

Generate a polite, empathetic acknowledgment response that:
1. Thanks the user for their feedback
2. Shows understanding of their concern
3. Indicates their feedback will be reviewed
4. Keep it concise and friendly (2-3 sentences max)

Response:"""

        response = self.llm.invoke(prompt)
        return response.content

    def generate_chat_response(
        self,
        user_message: str,
        relevant_feedbacks: List[Dict[str, Any]],
        product_filter: Optional[str] = None
    ) -> str:
        context_parts = []
        for i, fb in enumerate(relevant_feedbacks, 1):
            metadata = fb.get("metadata", {})
            product = metadata.get("product", "Unknown")
            user_id = metadata.get("user_id", "anonymous")
            timestamp = metadata.get("timestamp", "unknown")
            context_parts.append(
                f"{i}. [Product: {product}] [User: {user_id}] [Time: {timestamp}]\n   Feedback: {fb.get('text', '')}"
            )

        context = "\n\n".join(context_parts) if context_parts else "No feedback found."

        product_context = f" focusing on product '{product_filter}'" if product_filter else ""

        prompt = f"""You are a product insights assistant helping a product manager analyze user feedback.

The product manager asks: "{user_message}"

Here are the most relevant user feedbacks{product_context}:

{context}

Based on this feedback data, provide a helpful analysis that:
1. Answers the product manager's question
2. Identifies patterns, trends, or key issues
3. Provides actionable insights where possible
4. Be specific and reference actual feedback when relevant

If there isn't enough feedback to answer the question, be honest about it.

Response:"""

        response = self.llm.invoke(prompt)
        return response.content


llm_service = LLMService()