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
        Filter: Allow all conversation (User Request: 'use vectordb').
        Originally restricted to facts, now open for full history.
        """
        return True
    
    def add(self, text: str, metadata: dict = None):
        """Add to vector DB."""
        # Clean text if it matches specific 'remember' patterns
        clean_text = text
        for p in ["remember that ", "save this ", "remember "]:
            if text.lower().startswith(p):
                clean_text = text[len(p):].strip()
                break
                
        # Upsert
        import hashlib
        # Use deterministic ID based on content to prevent duplicates
        # This allows Safe Backfilling and Re-scanning of learning data
        doc_id = hashlib.md5(clean_text.encode(errors='ignore')).hexdigest()
        
        # Handle empty metadata for ChromaDB compatibility
        metadatas = [metadata] if metadata else None
        
        self.collection.upsert( # Changed from add to upsert for idempotency
            documents=[clean_text],
            metadatas=metadatas,
            ids=[doc_id]
        )
        return f"[Memory] Stored in VectorDB"

    def ingest_file(self, filepath: str):
        """Read and digest a text file into memory."""
        try:
            path = Path(filepath)
            if not path.exists() or not path.suffix == '.txt':
                return f"Skipped {path.name} (Not a text file)"
                
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if not content.strip():
                return "Empty file"
                
            # split into chunks? For now, index whole file or paragraphs.
            # Simple chunking by paragraph
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            count = 0
            for p in paragraphs:
                self.add(p, metadata={"source": path.name, "type": "learning_data"})
                count += 1
                
            return f"Ingested {count} chunks from {path.name}"
            
        except Exception as e:
            return f"Error ingesting {filepath}: {e}"

    def search(self, query: str, n_results=3, threshold=0.65) -> Optional[str]:
        """
        Search memory.
        Returns combined text of top N results if distance < threshold.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if not results['documents'][0]:
            return None
            
        valid_docs = []
        for i, text in enumerate(results['documents'][0]):
            dist = results['distances'][0][i]
            if dist <= threshold:
                # Deduplicate: Don't add if it's identical to query (approx)
                # Actually, sometimes the query IS the memory "I am from Haryana"
                # But if query is "Where am I from?" and memory is "User: Where am I from?", that's useless.
                # Let's keep it simple: Just add all valid matches. LLM can sift through.
                # Format: "Match 1: ... \n Match 2: ..."
                valid_docs.append(text)
        
        if not valid_docs:
            return None
            
        return "\n\n".join(valid_docs)
