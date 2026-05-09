import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from config.settings import settings
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY
        )
        self.collection = self.client.get_or_create_collection(
            name="feedbacks",
            metadata={"description": "User product feedback storage"}
        )

    def add_feedback(
        self,
        feedback_text: str,
        product: str,
        user_id: Optional[str] = None
    ) -> str:
        feedback_id = str(uuid.uuid4())
        metadata = {
            "product": product,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id or "anonymous"
        }

        self.collection.add(
            documents=[feedback_text],
            ids=[feedback_id],
            metadatas=[metadata]
        )

        return feedback_id

    def query(
        self,
        query_text: str,
        product_filter: Optional[str] = None,
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        where = {"product": product_filter} if product_filter else None

        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"]
        )

        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "text": doc,
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                })

        return formatted_results

    def get_all_feedbacks(self, product_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        where = {"product": product_filter} if product_filter else None

        results = self.collection.get(
            where=where,
            include=["documents", "metadatas"]
        )

        formatted_results = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"]):
                formatted_results.append({
                    "text": doc,
                    "metadata": results["metadatas"][i],
                    "id": results["ids"][i]
                })

        return formatted_results


vector_store = VectorStore()