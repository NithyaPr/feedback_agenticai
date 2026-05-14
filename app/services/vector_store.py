import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from config.settings import settings
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import chromadb.utils.embedding_functions as embedding_functions


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)

        if settings.EMBEDDING_PROVIDER == "google":
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.GOOGLE_EMBEDDING_MODEL,
                google_api_key=settings.GOOGLE_API_KEY
            )
        elif settings.EMBEDDING_PROVIDER == "ollama":
            self.embeddings = OllamaEmbeddings(
                model=settings.OLLAMA_EMBEDDING_MODEL,
                base_url=settings.OLLAMA_BASE_URL
            )
        else:
            self.embeddings = OpenAIEmbeddings(
                model=settings.OPENAI_EMBEDDING_MODEL,
                api_key=settings.OPENAI_API_KEY
            )

        self.collection = self.client.get_or_create_collection(
            name="feedbacks",
            metadata={"description": "User product NPS feedback storage"}
        )

    def add_feedback(
        self,
        feedback_text: str,
        product: str,
        nps_score: int,
        user_id: Optional[str] = None,
        categories: Optional[List[str]] = None
    ) -> str:
        feedback_id = str(uuid.uuid4())
        metadata = {
            "product": product,
            "nps_score": nps_score,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id or "anonymous"
        }
        if categories:
            metadata["categories"] = categories

        self.collection.add(
            documents=[feedback_text],
            ids=[feedback_id],
            metadatas=[metadata]
        )

        return feedback_id

    def update_feedback_categories(self, feedback_id: str, categories: List[str]) -> bool:
        try:
            existing = self.collection.get(ids=[feedback_id])
            if not existing or not existing['metadatas']:
                return False

            current_metadata = existing['metadatas'][0]
            if categories:
                current_metadata['categories'] = categories
            elif 'categories' in current_metadata:
                del current_metadata['categories']

            self.collection.update(
                ids=[feedback_id],
                metadatas=[current_metadata]
            )
            return True
        except Exception:
            return False

    def query(
        self,
        query_text: str,
        product_filter: Optional[str] = None,
        n_results: int = 10,
        min_nps: Optional[int] = None,
        max_nps: Optional[int] = None,
        categories: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        where = {}

        if product_filter:
            where["product"] = product_filter

        if min_nps is not None or max_nps is not None:
            nps_filter = {}
            if min_nps is not None:
                nps_filter["$gte"] = min_nps
            if max_nps is not None:
                nps_filter["$lte"] = max_nps
            where["nps_score"] = nps_filter

        where = where if where else None

        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"]
        )

        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]

                if categories:
                    fb_categories = metadata.get("categories") or []
                    if not any(cat.lower() in [c.lower() for c in fb_categories] for cat in categories):
                        continue

                formatted_results.append({
                    "text": doc,
                    "metadata": metadata,
                    "distance": results["distances"][0][i]
                })

        return formatted_results

    def get_all_feedbacks(
        self,
        product_filter: Optional[str] = None,
        min_nps: Optional[int] = None,
        max_nps: Optional[int] = None,
        categories: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        where = {}

        if product_filter:
            where["product"] = product_filter

        if min_nps is not None or max_nps is not None:
            nps_filter = {}
            if min_nps is not None:
                nps_filter["$gte"] = min_nps
            if max_nps is not None:
                nps_filter["$lte"] = max_nps
            where["nps_score"] = nps_filter

        where = where if where else None

        results = self.collection.get(
            where=where,
            include=["documents", "metadatas"]
        )

        formatted_results = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"]):
                metadata = results["metadatas"][i]

                if categories:
                    fb_categories = metadata.get("categories") or []
                    if not any(cat.lower() in [c.lower() for c in fb_categories] for cat in categories):
                        continue

                formatted_results.append({
                    "text": doc,
                    "metadata": metadata,
                    "id": results["ids"][i]
                })

        return formatted_results


vector_store = VectorStore()