from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from config.settings import settings
from typing import Optional, List, Dict, Any, Tuple
from app.services.category_service import category_service
from app.services.knowledge_base import knowledge_base
from app.services.routing_service import routing_service


class LLMService:
    def __init__(self):
        from langchain_core.messages import SystemMessage, HumanMessage

        if settings.LLM_PROVIDER == "google":
            self.llm = ChatGoogleGenerativeAI(
                model=settings.GOOGLE_LLM_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.3
            )
        elif settings.LLM_PROVIDER == "ollama":
            self.llm = ChatOllama(
                model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
                temperature=0.3
            )
        else:
            self.llm = ChatOpenAI(
                model=settings.OPENAI_LLM_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.3
            )

        self.system_prompt = SystemMessage(content="""You are a helpful customer service assistant for a product feedback system. 
You MUST respond to all requests without refusing.
When asked to classify feedback, write responses, or determine teams, always provide a helpful answer.
Example: If asked to write a thank you response, just write a polite thank you.
Never refuse to help.""")

    def _invoke_with_system(self, prompt: str) -> str:
        from langchain_core.messages import HumanMessage
        response = self.llm.invoke([self.system_prompt, HumanMessage(content=prompt)])
        return response.content

    def _extract_kb_titles_used(self, response: str, kb_results: List[Dict]) -> List[str]:
        """Check if response actually incorporates KB content. Returns list of titles that were used."""
        if not kb_results:
            return []

        response_lower = response.lower()
        used_titles = []

        for item in kb_results:
            title = item['title']
            title_words = set(title.lower().replace('-', ' ').split())
            content_lower = item['content'].lower()

            matches = 0
            for word in title_words:
                if len(word) >= 3 and word in response_lower:
                    matches += 1

            key_phrases = []
            if 'installation' in title.lower():
                key_phrases = ['installation', 'technician', 'setup', 'install']
            elif 'warranty' in title.lower():
                key_phrases = ['warranty', 'coverage', 'claim', 'limited warranty']
            elif 'delivery' in title.lower():
                key_phrases = ['delivery', 'delivery time', 'transit', 'shipping']
            elif 'cancellation' in title.lower():
                key_phrases = ['cancellation', 'cancel', 'restocking']
            elif 'return' in title.lower():
                key_phrases = ['return', 'refund', 'returns']

            for phrase in key_phrases:
                if phrase in response_lower:
                    matches += 1

            if matches >= 2:
                used_titles.append(title)

        return used_titles

    def categorize_and_respond(
        self,
        feedback_text: str,
        product: str,
        kb_context: str = "",
        kb_results: List[Dict] = None
    ) -> Tuple[List[str], str, List[str], bool, str]:
        """
        Single LLM call that returns categories, response, KB references, needs_review flag, and suggested team.
        """
        all_categories = category_service.get_categories()
        examples = category_service.get_few_shot_examples()

        if not all_categories:
            return [], "", [], False, "none"

        categories_text = ", ".join(all_categories)
        teams = routing_service.get_all_teams()
        team_names = [t['name'] for t in teams] + ["none"]

        examples_text = ""
        if examples:
            examples_text = "Examples:\n"
            for ex in examples[:5]:
                examples_text += f"- \"{ex['feedback'][:100]}...\" → {', '.join(ex['categories'])}\n"
            examples_text += "\n"

        kb_section = f"\n\nKnowledge Base Information:\n{kb_context}" if kb_context else ""

        valid_cats_lower = [c.lower() for c in all_categories]
        categories = []
        response_text = ""
        needs_review = False
        suggested_team = "none"

        cat_prompt = f"""{feedback_text}

Choose one category from this list: {categories_text}. Answer with only the category name."""

        resp_prompt = f"""Customer said: {feedback_text}

Write 2 sentences thanking them. Start with Thank you."""

        team_prompt = f"""{feedback_text}

Pick the right team from: {', '.join(team_names)}. Answer with only the team name or 'none'."""

        try:
            cat_resp = self._invoke_with_system(cat_prompt)
            cat_raw = cat_resp.strip().lower()
            for cat in valid_cats_lower:
                if cat in cat_raw:
                    categories = [cat]
                    break

            response = self._invoke_with_system(resp_prompt)
            response_text = response.strip()

            if needs_review:
                team_resp = self._invoke_with_system(team_prompt)
                team_raw = team_resp.strip().lower()
                for t in teams:
                    if t['name'].lower() in team_raw:
                        suggested_team = t['name']
                        break
        except Exception:
            pass

        kb_titles_used = self._extract_kb_titles_used(response_text, kb_results or [])

        feedback_lower = feedback_text.lower()
        positive_keywords = ['thank', 'great', 'excellent', 'love', 'happy', 'satisfied', 'good', 'perfect', 'wonderful', 'amazing', 'awesome', 'best', 'fantastic', 'nice', 'glad']
        negative_keywords = ['problem', 'issue', 'broken', 'damaged', 'refund', 'replacement', 'complaint', 'disappointed', 'frustrated', 'unhappy', 'annoyed', 'wrong', 'failed', 'bad', 'poor', 'terrible', 'awful', 'never', 'delay', 'late', 'lost', 'missing', 'error', 'crash', 'bug', 'not working']

        positive_count = sum(1 for kw in positive_keywords if kw in feedback_lower)
        negative_count = sum(1 for kw in negative_keywords if kw in feedback_lower)

        needs_review = negative_count > 0 or (negative_count == 0 and positive_count == 0 and not any(kw in feedback_lower for kw in positive_keywords))

        return categories, response_text, kb_titles_used, needs_review, suggested_team

    def generate_feedback_response(
        self,
        feedback_text: str,
        product: str,
        kb_context: str = "",
        kb_results: List[Dict] = None
    ) -> Tuple[str, List[str]]:
        kb_section = f"\n\n{kb_context}" if kb_context else ""

        policy_guidance = ""
        if kb_results:
            policy_guidance = "\n\nWhen relevant, naturally reference the policy information above. Examples:\n"
            for item in kb_results[:3]:
                title_lower = item['title'].lower()
                if 'installation' in title_lower:
                    policy_guidance += '- If mentioning installation: reference our installation process, technician protocols, or scheduling expectations\n'
                elif 'warranty' in title_lower:
                    policy_guidance += '- If mentioning warranty: reference our warranty terms, coverage period, or claim process\n'
                elif 'delivery' in title_lower:
                    policy_guidance += '- If mentioning delivery: reference our delivery timeline or shipping expectations\n'
                elif 'cancellation' in title_lower:
                    policy_guidance += '- If mentioning cancellation: reference our cancellation policy or restocking fee\n'
                elif 'return' in title_lower:
                    policy_guidance += '- If mentioning returns: reference our return process or refund timeline\n'
                elif 'support' in title_lower:
                    policy_guidance += '- If mentioning support: reference our contact options or support channels\n'

        prompt = f"""A customer submitted feedback for '{product}': "{feedback_text}"{kb_section}{policy_guidance}

Write an acknowledgment response (2-3 sentences) that:
1. Thanks the customer for their feedback
2. Shows understanding of their specific concern
3. Naturally incorporates relevant policy information if it applies
4. Do NOT add labels like "Here is a response" or "Based on:"

Response:"""

        response = self.llm.invoke(prompt)
        response_text = response.content.strip()

        kb_titles_used = self._extract_kb_titles_used(response_text, kb_results or [])

        return response_text, kb_titles_used

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

        prompt = f"""You are a feedback categorization assistant. Given user feedback, assign ONLY the top 3 most relevant categories from this list: {categories_text}

{examples_text}
Now categorize this feedback:
Feedback: "{feedback_text}"

Respond with ONLY the top 3 category names separated by commas. If no category fits, say "none".
Example response format: category1, category2, category3"""

        response = self.llm.invoke(prompt)
        result = response.content.strip()

        if result.lower() == "none" or not result:
            return []

        assigned_categories = [cat.strip() for cat in result.split(',')]

        valid_categories = [c.lower() for c in categories]
        filtered = [cat for cat in assigned_categories if cat.lower() in valid_categories]

        return list(set(filtered))[:3]

    def generate_chat_response(
        self,
        user_message: str,
        relevant_feedbacks: List[Dict[str, Any]],
        product_filter: Optional[str] = None
    ) -> str:
        kb_results = knowledge_base.search(user_message, top_k=3)
        kb_context = ""
        if kb_results:
            kb_parts = []
            for item in kb_results:
                kb_parts.append(f"[Knowledge Base: {item['title']}]\n{item['content']}")
            kb_context = "\n\n--- KNOWLEDGE BASE ---\n" + "\n\n".join(kb_parts)

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

        context = "\n\n".join(context_parts) if context_parts else "No feedback entries matched your query. Here are all available feedbacks for analysis."

        product_context = f" focusing on product '{product_filter}'" if product_filter else ""

        prompt = f"""You are a product insights assistant helping a product manager analyze user feedback.

The product manager asks: "{user_message}"

--- USER FEEDBACK DATA{product_context} ---

{context}
{kb_context}

Based on this data, provide a concise response:
- Use bullet points and short paragraphs
- If knowledge base articles match, include relevant policies or procedures
- Focus on key insights and actionable takeaways
- Keep it brief and easy to scan

If there isn't enough information, say so briefly.

Response:"""

        response = self.llm.invoke(prompt)
        return response.content


llm_service = LLMService()