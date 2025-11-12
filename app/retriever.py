"""
RAG Retriever for NovaCRM Knowledge Base

Provides semantic search over NovaCRM documentation using FAISS
"""

from pathlib import Path
from typing import List, Dict, Any
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_PATH = BASE_DIR / "index" / "faiss_index"

class KnowledgeBaseRetriever:
    """
    Retriever for NovaCRM knowledge base using FAISS vector store
    """
    
    def __init__(self):
        """Initialize retriever with FAISS index"""
        if not INDEX_PATH.exists():
            raise FileNotFoundError(
                f"FAISS index not found at {INDEX_PATH}. "
                f"Please run scripts/build_index.py first."
            )
        
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = FAISS.load_local(
            str(INDEX_PATH),
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 5}
        )
    
    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of Document objects with content and metadata
        """
        self.retriever.search_kwargs["k"] = k
        return self.retriever.invoke(query)
    
    def retrieve_with_scores(self, query: str, k: int = 5) -> List[tuple]:
        """
        Retrieve documents with similarity scores
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of (Document, score) tuples
        """
        return self.vectorstore.similarity_search_with_score(query, k=k)
    
    def format_results(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Format retrieval results for use in prompts
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Dict with formatted results and metadata
        """
        formatted_docs = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get('source', 'unknown')
            formatted_docs.append({
                "id": i,
                "content": doc.page_content,
                "source": Path(source).name if source != 'unknown' else source
            })
        
        context = "\n\n".join([
            f"[Document {doc['id']} - {doc['source']}]\n{doc['content']}"
            for doc in formatted_docs
        ])
        
        return {
            "context": context,
            "documents": formatted_docs,
            "count": len(formatted_docs)
        }

def get_retriever() -> KnowledgeBaseRetriever:
    """
    Factory function to get retriever instance
    
    Returns:
        KnowledgeBaseRetriever instance
    """
    return KnowledgeBaseRetriever()

