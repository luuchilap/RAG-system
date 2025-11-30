"""
RAG (Retrieval-Augmented Generation) service.
Handles querying FAISS indices to retrieve relevant document chunks.
"""
import os
from typing import List, Dict, Any, Optional
from uuid import UUID
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from app.config import settings


class RAGService:
    """Service for RAG document retrieval."""
    
    def __init__(self):
        """Initialize the RAG service with embeddings."""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set in environment variables")
        
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def _get_user_index_path(self, user_id: UUID) -> str:
        """Get the path to a user's FAISS index directory."""
        return os.path.join(
            settings.FAISS_INDEX_FOLDER,
            f"user_{user_id}"
        )
    
    async def load_user_index(self, user_id: UUID) -> Optional[FAISS]:
        """
        Load a user's FAISS index from the file system.
        
        Args:
            user_id: ID of the user
        
        Returns:
            FAISS vectorstore if index exists, None otherwise
        """
        user_index_path = self._get_user_index_path(user_id)
        
        # Check if index directory exists
        if not os.path.exists(user_index_path):
            return None
        
        # Check if index files exist (FAISS saves as directory with .faiss and .pkl files)
        index_files = os.listdir(user_index_path) if os.path.isdir(user_index_path) else []
        if not any(f.endswith('.faiss') for f in index_files):
            return None
        
        try:
            vectorstore = FAISS.load_local(
                user_index_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            return vectorstore
        except Exception as e:
            print(f"Error loading FAISS index for user {user_id}: {str(e)}")
            return None
    
    async def query_documents(
        self,
        user_id: UUID,
        query_text: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Query a user's documents to retrieve relevant chunks.
        
        Args:
            user_id: ID of the user
            query_text: Query text to search for
            top_k: Number of results to return
        
        Returns:
            List of dictionaries containing text, metadata, and relevance_score
        """
        # Load user's index
        vectorstore = await self.load_user_index(user_id)
        
        if not vectorstore:
            return []
        
        try:
            # Query the index with similarity search
            # Note: FAISS similarity_search_with_score returns (Document, score) tuples
            # Lower scores indicate higher similarity (distance-based)
            results = vectorstore.similarity_search_with_score(
                query_text,
                k=top_k
            )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                # Extract user_id from metadata to ensure user isolation
                doc_user_id = doc.metadata.get("user_id")
                
                # Double-check user isolation (metadata should already be filtered)
                if doc_user_id and str(doc_user_id) != str(user_id):
                    continue  # Skip documents that don't belong to this user
                
                formatted_results.append({
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": float(score),
                })
            
            return formatted_results
        except Exception as e:
            print(f"Error querying documents for user {user_id}: {str(e)}")
            return []

