"""Vector memory and long-term memory system with semantic search."""

import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class MemoryItem:
    """A single memory item with embeddings."""
    
    def __init__(
        self,
        content: str,
        memory_type: str = "general",  # conversation, learning, fact, feedback
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict] = None,
        id: Optional[str] = None
    ):
        self.id = id or hashlib.md5(content.encode()).hexdigest()[:8]
        self.content = content
        self.memory_type = memory_type
        self.embedding = embedding
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        self.access_count = 0
        self.importance = metadata.get("importance", 0.5) if metadata else 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type,
            "embedding": self.embedding,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "access_count": self.access_count,
            "importance": self.importance
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "MemoryItem":
        """Create from dictionary."""
        item = cls(
            content=data["content"],
            memory_type=data.get("memory_type", "general"),
            embedding=data.get("embedding"),
            metadata=data.get("metadata", {})
        )
        item.id = data.get("id", item.id)
        item.access_count = data.get("access_count", 0)
        item.importance = data.get("importance", 0.5)
        if "timestamp" in data:
            item.timestamp = datetime.fromisoformat(data["timestamp"])
        return item


class EmbeddingModel:
    """Interface for embedding models."""
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            list: Embedding vector
        """
        raise NotImplementedError
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts
            
        Returns:
            list: List of embeddings
        """
        embeddings = []
        for text in texts:
            embeddings.append(await self.embed_text(text))
        return embeddings


class SentenceTransformerEmbedding(EmbeddingModel):
    """Embedding using sentence-transformers library."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Loaded embedding model: {model_name}")
        except ImportError:
            logger.error("sentence-transformers not installed")
            raise
    
    async def embed_text(self, text: str) -> List[float]:
        """Embed text using sentence-transformers."""
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts."""
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist()


class VectorMemory:
    """Vector-based memory system with semantic search."""
    
    def __init__(
        self,
        embedding_model: Optional[EmbeddingModel] = None,
        storage_path: Optional[str] = None,
        similarity_threshold: float = 0.5
    ):
        self.embedding_model = embedding_model
        self.storage_path = Path(storage_path) if storage_path else Path("./memory")
        self.storage_path.mkdir(exist_ok=True)
        self.similarity_threshold = similarity_threshold
        
        # In-memory storage
        self.memories: Dict[str, MemoryItem] = {}
        self.memory_index: List[str] = []  # For efficient querying
        
        # Load existing memories
        self._load_from_disk()
    
    async def add_memory(
        self,
        content: str,
        memory_type: str = "general",
        metadata: Optional[Dict] = None
    ) -> str:
        """Add a memory item.
        
        Args:
            content: Memory content
            memory_type: Type of memory
            metadata: Additional metadata
            
        Returns:
            str: Memory ID
        """
        # Generate embedding if model available
        embedding = None
        if self.embedding_model:
            embedding = await self.embedding_model.embed_text(content)
        
        memory = MemoryItem(
            content=content,
            memory_type=memory_type,
            embedding=embedding,
            metadata=metadata
        )
        
        self.memories[memory.id] = memory
        self.memory_index.append(memory.id)
        
        # Save to disk
        self._save_to_disk()
        
        logger.info(f"Added memory: {memory.id} ({memory_type})")
        return memory.id
    
    async def search(
        self,
        query: str,
        memory_type: Optional[str] = None,
        limit: int = 5,
        use_embedding: bool = True
    ) -> List[Tuple[MemoryItem, float]]:
        """Search memories using semantic similarity.
        
        Args:
            query: Search query
            memory_type: Filter by memory type
            limit: Maximum results
            use_embedding: Use embedding-based search if available
            
        Returns:
            list: List of (MemoryItem, similarity_score) tuples
        """
        if not self.memories:
            return []
        
        results = []
        
        # Embedding-based search
        if use_embedding and self.embedding_model:
            try:
                query_embedding = await self.embedding_model.embed_text(query)
                
                for memory_id in self.memory_index:
                    memory = self.memories[memory_id]
                    
                    # Filter by type if specified
                    if memory_type and memory.memory_type != memory_type:
                        continue
                    
                    if memory.embedding:
                        similarity = self._cosine_similarity(query_embedding, memory.embedding)
                        
                        if similarity >= self.similarity_threshold:
                            results.append((memory, similarity))
                
                # Sort by similarity score
                results.sort(key=lambda x: x[1], reverse=True)
                return results[:limit]
            
            except Exception as e:
                logger.error(f"Embedding search error: {str(e)}")
        
        # Fallback to text-based search
        query_lower = query.lower()
        for memory_id in self.memory_index:
            memory = self.memories[memory_id]
            
            if memory_type and memory.memory_type != memory_type:
                continue
            
            if query_lower in memory.content.lower():
                # Simple text match scoring
                score = len(query_lower) / len(memory.content)
                results.append((memory, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
    
    async def get_context(
        self,
        query: str,
        max_results: int = 3,
        memory_type: Optional[str] = None
    ) -> str:
        """Get context string from similar memories.
        
        Args:
            query: Query string
            max_results: Maximum memories to include
            memory_type: Filter by memory type
            
        Returns:
            str: Context string for LLM
        """
        results = await self.search(query, memory_type, max_results)
        
        if not results:
            return ""
        
        context_parts = ["Relevant memories:"]
        for memory, score in results:
            memory.access_count += 1
            context_parts.append(f"- [{memory.memory_type}] {memory.content}")
        
        self._save_to_disk()
        return "\n".join(context_parts)
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import math
        
        if not vec1 or not vec2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _save_to_disk(self) -> None:
        """Persist memories to disk."""
        try:
            memories_data = [memory.to_dict() for memory in self.memories.values()]
            
            with open(self.storage_path / "memories.json", "w") as f:
                json.dump(memories_data, f, indent=2)
            
            logger.debug(f"Saved {len(memories_data)} memories to disk")
        except Exception as e:
            logger.error(f"Error saving memories: {str(e)}")
    
    def _load_from_disk(self) -> None:
        """Load memories from disk."""
        try:
            memories_file = self.storage_path / "memories.json"
            
            if memories_file.exists():
                with open(memories_file, "r") as f:
                    memories_data = json.load(f)
                
                for data in memories_data:
                    memory = MemoryItem.from_dict(data)
                    self.memories[memory.id] = memory
                    self.memory_index.append(memory.id)
                
                logger.info(f"Loaded {len(self.memories)} memories from disk")
        except Exception as e:
            logger.error(f"Error loading memories: {str(e)}")
    
    def clear(self) -> None:
        """Clear all memories."""
        self.memories.clear()
        self.memory_index.clear()
        self._save_to_disk()
        logger.info("Cleared all memories")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        type_count = {}
        total_importance = 0
        total_accesses = 0
        
        for memory in self.memories.values():
            type_count[memory.memory_type] = type_count.get(memory.memory_type, 0) + 1
            total_importance += memory.importance
            total_accesses += memory.access_count
        
        return {
            "total_memories": len(self.memories),
            "type_distribution": type_count,
            "average_importance": total_importance / len(self.memories) if self.memories else 0,
            "total_accesses": total_accesses,
            "storage_path": str(self.storage_path)
        }
    
    def export_memories(self, filepath: str, format: str = "json") -> None:
        """Export memories to file.
        
        Args:
            filepath: Output file path
            format: Export format (json, csv)
        """
        try:
            if format == "json":
                memories_data = [memory.to_dict() for memory in self.memories.values()]
                with open(filepath, "w") as f:
                    json.dump(memories_data, f, indent=2)
            
            elif format == "csv":
                import csv
                with open(filepath, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Type", "Content", "Importance", "Accesses", "Timestamp"])
                    for memory in self.memories.values():
                        writer.writerow([
                            memory.id,
                            memory.memory_type,
                            memory.content[:100],
                            memory.importance,
                            memory.access_count,
                            memory.timestamp
                        ])
            
            logger.info(f"Exported memories to {filepath}")
        except Exception as e:
            logger.error(f"Error exporting memories: {str(e)}")
