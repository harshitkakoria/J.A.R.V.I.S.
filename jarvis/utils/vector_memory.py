import chromadb
from chromadb.utils import embedding_functions
import re
from typing import List, Tuple, Optional

class VectorMemory:
    """
    Long-term memory using ChromaDB.
    Strictly follows:
    1. Selective Storage (only 'remember' commands or facts)
    2. Probabilistic Retrieval (returns score)
    """
    
    def __init__(self, path="data/chroma_db"):
        self.client = chromadb.PersistentClient(path=path)
        
        # Use a lightweight, standard model
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        self.collection = self.client.get_or_create_collection(
            name="jarvis_memory",
            embedding_function=self.ef,
            metadata={"hnsw:space": "cosine"} # Use cosine similarity
        )
        
        # Strict patterns for what to store
        self.storage_patterns = [
            r"remember that",
            r"remember my",
            r"save this",
            r"my name is",
            r"i am a",
            r"my .* is", # "My favorite color is..."
            r"i like",
            r"i prefer"
        ]

    def should_store(self, text: str) -> bool:
        """
        Filter: Only allow explicit facts/preferences.
        """
        text = text.lower()
        
        # 1. Check explicit patterns
        if any(re.search(p, text) for p in self.storage_patterns):
            return True
            
        # 2. Reject casual chit-chat
        # (Implicitly rejected if not matching above)
        
        return False
    
    def add(self, text: str, metadata: dict = None):
        """Add to vector DB if it passes filters."""
        if not self.should_store(text):
            return "[Memory] Ignored (Not a fact/preference)"
            
        # Clean text for storage (remove "remember that")
        clean_text = text
        for p in ["remember that ", "save this ", "remember "]:
            if text.lower().startswith(p):
                clean_text = text[len(p):].strip()
                break
                
        # Upsert
        # We need a unique ID. Using hash of text.
        import hashlib
        doc_id = hashlib.md5(clean_text.encode()).hexdigest()
        
        self.collection.upsert(
            documents=[clean_text],
            metadatas=[metadata or {}],
            ids=[doc_id]
        )
        return f"[Memory] Stored: {clean_text}"

    def search(self, query: str, n_results=1, threshold=0.3) -> Optional[Tuple[str, float]]:
        """
        Search memory.
        Returns (text, distance) if distance < threshold.
        Note: With 'cosine', distance is 1 - similarity.
        So Distance 0.1 means 0.9 similarity (Very good).
        Distance 0.4 means 0.6 similarity.
        Threshold 0.4 is a reasonable strictness.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if not results['documents'][0]:
            return None
            
        text = results['documents'][0][0]
        distance = results['distances'][0][0]
        
        # User Rule: if result.score < X: ignore
        # Chroma 'cosine' distance: LOWER is BETTER (0 = identical, 1 = opposite)
        # So we reject if distance > threshold
        
        if distance > threshold:
            return None
            
        return (text, distance)
