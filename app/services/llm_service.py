from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from config.settings import settings
from typing import Optional, List, Dict, Any
from app.services.category_service import category_service


class LLMService:
    def __init__(self):
        if settings.LLM_PROVIDER == "google":
            self.llm = ChatGoogleGenerativeAI(
                model=settings.GOOGLE_LLM_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.7
            )
        elif settings.LLM_PROVIDER == "ollama":
            self.llm = ChatOllama(
                model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
                temperature=0.7
            )
        else:
            self.llm = ChatOpenAI(
                model=settings.OPENAI_LLM_MODEL,
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

    def categorize_feedback(self, feedback_text: str) -> List[str]:
        categories = category_service.get_categories()
        examples = category_service.get_few_shot_examples()

        if not categories:
            return []

        categories_text = ", ".join(categories)

        examples_text = ""
        if examples:
            examples_text = "Here are some examples:\n"
            for ex in examples:
                examples_text += f"- Feedback: \"{ex['feedback']}\" → Categories: {', '.join(ex['categories'])}\n"
            examples_text += "\n"

        prompt = f"""You are a feedback categorization assistant. Given user feedback, assign relevant categories from this list: {categories_text}

{examples_text}
Now categorize this feedback:
Feedback: "{feedback_text}"

Respond with ONLY the category names separated by commas. If no category fits, say "none".
Example response format: category1, category2, category3"""

        response = self.llm.invoke(prompt)
        result = response.content.strip()

        if result.lower() == "none" or not result:
            return []

        assigned_categories = [cat.strip() for cat in result.split(',')]

        valid_categories = [c.lower() for c in categories]
        filtered = [cat for cat in assigned_categories if cat.lower() in valid_categories]

        return list(set(filtered))

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
            nps = metadata.get("nps_score", "N/A")
            categories = metadata.get("categories", [])
            cats_str = f" [{', '.join(categories)}]" if categories else ""
            context_parts.append(
                f"{i}. [Product: {product}] [NPS: {nps}]{cats_str} [User: {user_id}] [Time: {timestamp}]\n   Feedback: {fb.get('text', '')}"
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