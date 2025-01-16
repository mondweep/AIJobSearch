import faiss
import numpy as np
import sqlite3
import json
import os
from pathlib import Path
import hashlib
from datetime import datetime
import pickle

class EmbeddingCache:
    def __init__(self, cache_dir="cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize FAISS index
        self.index_path = self.cache_dir / "embeddings.index"
        self.dimension = 1536  # OpenAI embedding dimension
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
        
        # Initialize SQLite database
        self.db_path = self.cache_dir / "metadata.db"
        self.init_db()
    
    def init_db(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text_hash TEXT UNIQUE,
                    text TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def get_text_hash(self, text):
        """Generate hash for text"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    def get_cached_embedding(self, text):
        """Get cached embedding if exists"""
        text_hash = self.get_text_hash(text)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id FROM embeddings WHERE text_hash = ?",
                (text_hash,)
            )
            result = cursor.fetchone()
            
            if result:
                # Get the embedding from FAISS
                embedding_id = result[0] - 1  # FAISS is 0-based
                embeddings = self.index.reconstruct_n(embedding_id, 1)
                return embeddings[0]
        
        return None
    
    def cache_embedding(self, text, embedding, metadata=None):
        """Cache embedding and metadata"""
        text_hash = self.get_text_hash(text)
        
        # Add to FAISS index
        self.index.add(np.array([embedding]))
        
        # Add to SQLite
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO embeddings (text_hash, text, metadata)
                    VALUES (?, ?, ?)
                    """,
                    (text_hash, text, json.dumps(metadata) if metadata else None)
                )
                conn.commit()
            except sqlite3.IntegrityError:
                # Text already exists, update instead
                conn.execute(
                    """
                    UPDATE embeddings 
                    SET metadata = ?
                    WHERE text_hash = ?
                    """,
                    (json.dumps(metadata) if metadata else None, text_hash)
                )
                conn.commit()
        
        # Save FAISS index
        faiss.write_index(self.index, str(self.index_path))
    
    def search_similar(self, embedding, k=5):
        """Search for similar embeddings"""
        if self.index.ntotal == 0:
            return []
            
        # Search FAISS index
        D, I = self.index.search(np.array([embedding]), k)
        
        # Get metadata for results
        results = []
        with sqlite3.connect(self.db_path) as conn:
            for idx, distance in zip(I[0], D[0]):
                if idx != -1:  # Valid index
                    cursor = conn.execute(
                        "SELECT text, metadata FROM embeddings WHERE id = ?",
                        (idx + 1,)  # SQLite is 1-based
                    )
                    text, metadata = cursor.fetchone()
                    results.append({
                        'text': text,
                        'metadata': json.loads(metadata) if metadata else None,
                        'distance': float(distance)
                    })
        
        return results
    
    def clear_cache(self):
        """Clear all cached embeddings"""
        # Clear FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        faiss.write_index(self.index, str(self.index_path))
        
        # Clear SQLite database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM embeddings")
            conn.commit()
