"""OpenAI API response caching utility."""

import json
import hashlib
from pathlib import Path
from typing import Any, Optional, Dict


class APICache:
    """Simple cache for API responses."""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_key(self, prompt: str) -> str:
        """Generate cache key from prompt."""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def get(self, prompt: str) -> Optional[str]:
        """Get cached response if available."""
        cache_file = self.cache_dir / f"{self._get_cache_key(prompt)}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                    return data.get("response")
            except (json.JSONDecodeError, IOError):
                return None
        
        return None
    
    def set(self, prompt: str, response: str) -> None:
        """Cache API response."""
        cache_file = self.cache_dir / f"{self._get_cache_key(prompt)}.json"
        
        try:
            with open(cache_file, "w") as f:
                json.dump({"prompt": prompt, "response": response}, f)
        except IOError:
            pass
    
    def clear(self) -> None:
        """Clear all cached responses."""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
