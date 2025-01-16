import os
import json
import hashlib
from pathlib import Path
import pickle
from datetime import datetime
import shutil

class FileCache:
    def __init__(self, cache_dir="file_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.cache_dir / "metadata.json"
        self._load_metadata()
        
        # Default expiry time (24 hours in seconds)
        self.expiry_time = 24 * 60 * 60
    
    def _load_metadata(self):
        """Load cache metadata from file"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
    
    def _save_metadata(self):
        """Save cache metadata to file"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _get_file_hash(self, file_path):
        """Generate hash for a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read the file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _get_cache_path(self, file_hash, file_type):
        """Get path for cached file"""
        return self.cache_dir / f"{file_type}_{file_hash}.pkl"
    
    def _hash_key(self, key):
        """Hash a cache key to create a filename-safe string"""
        # Create a hash of the key
        key_hash = hashlib.sha256(str(key).encode()).hexdigest()
        return key_hash[:32]  # Use first 32 chars of hash for filename
    
    def _is_expired(self, key):
        """Check if a cache entry is expired"""
        if key not in self.metadata:
            return True
            
        timestamp = self.metadata[key].get('timestamp')
        if not timestamp:
            return True
            
        age = datetime.now().timestamp() - timestamp
        return age > self.expiry_time
    
    def get_cached_profile(self, file_paths):
        """
        Get cached profile data for a set of files
        file_paths: dict of file types to file paths
        """
        # Generate composite hash of all files
        file_hashes = {
            file_type: self._get_file_hash(path)
            for file_type, path in file_paths.items()
            if path and os.path.exists(path)
        }
        
        # Check if all files are cached with same hash
        for file_type, file_hash in file_hashes.items():
            cache_key = f"{file_type}_{file_hash}"
            if cache_key not in self.metadata:
                print(f"Cache miss for {file_type}")
                return None
                
            cache_path = self._get_cache_path(file_hash, file_type)
            if not cache_path.exists():
                print(f"Cache file missing for {file_type}")
                return None
        
        # All files are cached, load and combine data
        cached_data = {}
        for file_type, file_hash in file_hashes.items():
            cache_path = self._get_cache_path(file_hash, file_type)
            try:
                with open(cache_path, 'rb') as f:
                    cached_data[file_type] = pickle.load(f)
                print(f"Cache hit for {file_type}")
            except Exception as e:
                print(f"Error loading cache for {file_type}: {str(e)}")
                return None
        
        return cached_data
    
    def cache_profile(self, file_paths, parsed_data):
        """
        Cache parsed profile data for a set of files
        file_paths: dict of file types to file paths
        parsed_data: dict of file types to parsed data
        """
        for file_type, file_path in file_paths.items():
            if not file_path or not os.path.exists(file_path):
                continue
                
            file_hash = self._get_file_hash(file_path)
            cache_path = self._get_cache_path(file_hash, file_type)
            
            # Save parsed data
            with open(cache_path, 'wb') as f:
                pickle.dump(parsed_data.get(file_type), f)
            
            # Update metadata
            self.metadata[f"{file_type}_{file_hash}"] = {
                'original_path': str(file_path),
                'cached_at': datetime.now().isoformat(),
                'file_size': os.path.getsize(file_path)
            }
            
            print(f"Cached {file_type} data")
        
        self._save_metadata()
    
    def clear_cache(self):
        """Clear all cached files"""
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata = {}
        
    def get(self, key):
        """Get value from cache"""
        key_hash = self._hash_key(key)
        cache_path = self.cache_dir / f"{key_hash}.pkl"
        
        # Check if cache exists and is not expired
        if cache_path.exists() and not self._is_expired(key_hash):
            try:
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
            except Exception:
                # If there's any error loading the cache, treat it as a miss
                return None
        return None
    
    def set(self, key, value):
        """Set value in cache with current timestamp"""
        key_hash = self._hash_key(key)
        cache_path = self.cache_dir / f"{key_hash}.pkl"
        
        # Save the value
        with open(cache_path, 'wb') as f:
            pickle.dump(value, f)
        
        # Update metadata with timestamp
        self.metadata[key_hash] = {
            'timestamp': datetime.now().timestamp(),
            'key': key
        }
        self._save_metadata()
