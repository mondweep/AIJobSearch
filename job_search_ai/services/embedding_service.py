from openai import OpenAI
from utils.embedding_cache import EmbeddingCache
import numpy as np
import os

class EmbeddingService:
    def __init__(self, cache_dir="cache"):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.cache = EmbeddingCache(cache_dir)
    
    def get_embedding(self, text, metadata=None, use_cache=True):
        """Get embedding for text, using cache if available"""
        if not text:
            print("Debug: Empty text, returning zero vector")
            return np.zeros(1536)  # Return zero vector for empty text
            
        if use_cache:
            cached_embedding = self.cache.get_cached_embedding(text)
            if cached_embedding is not None:
                print("Debug: Cache hit for text:", text[:50], "...")
                return cached_embedding
            print("Debug: Cache miss for text:", text[:50], "...")
        
        try:
            print("Debug: Getting embedding from OpenAI for text:", text[:50], "...")
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            embedding = response.data[0].embedding
            
            if use_cache:
                print("Debug: Caching embedding for text:", text[:50], "...")
                self.cache.cache_embedding(text, embedding, metadata)
            
            return embedding
        except Exception as e:
            print(f"Error getting embedding: {str(e)}")
            return np.zeros(1536)  # Return zero vector on error
    
    def get_embeddings(self, texts, metadata=None, use_cache=True):
        """Get embeddings for multiple texts"""
        return [self.get_embedding(text, meta, use_cache) 
                for text, meta in zip(texts, metadata or [None] * len(texts))]
    
    def search_similar(self, embedding, k=5):
        """Search for similar texts using cached embeddings"""
        return self.cache.search_similar(embedding, k)
    
    def clear_cache(self):
        """Clear the embedding cache"""
        self.cache.clear_cache()
