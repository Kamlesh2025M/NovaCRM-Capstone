from pathlib import Path
from typing import Dict, Any, List

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

def kb_search(query: str, k: int = 5) -> Dict[str, Any]:
    """
    Search knowledge base documents using simple keyword matching.
    Returns top k most relevant chunks.
    This is a fallback implementation; the main RAG uses FAISS.
    """
    try:
        kb_path = BASE_DIR / "data" / "kb"
        if not kb_path.exists():
            return {
                "error": f"Knowledge base not found at {kb_path}",
                "explanation": "KB folder is missing",
                "source": str(kb_path)
            }
        
        results = []
        query_lower = query.lower()
        
        for md_file in kb_path.glob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if query_lower in content.lower():
                    lines = content.split('\n')
                    relevant_lines = [line for line in lines if query_lower in line.lower()]
                    results.append({
                        "document": md_file.name,
                        "content": content[:500],
                        "matches": relevant_lines[:3]
                    })
        
        results = results[:k]
        
        return {
            "query": query,
            "results_count": len(results),
            "results": results,
            "explanation": f"Found {len(results)} documents matching '{query}'",
            "source": str(kb_path)
        }
    
    except Exception as e:
        return {
            "error": f"{type(e).__name__}: {str(e)}",
            "explanation": "Error searching knowledge base",
            "source": str(kb_path)
        }

