"""
embeddings.py
Embedding generation and vector search for TechDocAgent Advanced.

Provides:
- Generate embeddings for code chunks using Gemini
- Store embeddings in FAISS vector database
- Semantic search and retrieval
- Similarity-based code lookup
"""

import os
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import google.generativeai as genai


try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("Warning: FAISS not installed. Vector search will be limited.")


class EmbeddingManager:
    """
    Manages embeddings and vector search for code chunks.

    Features:
    - Generate embeddings using Gemini
    - Store embeddings in FAISS index
    - Semantic search for relevant code
    - Persist and load embeddings
    """

    def __init__(self, api_key: Optional[str] = None, index_path: str = ".techdoc_embeddings"):
        """
        Initialize embedding manager.

        Args:
            api_key: Gemini API key (or uses GEMINI_API_KEY env var)
            index_path: Directory to store FAISS index and metadata
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)

        self.index_path = Path(index_path)
        self.index_path.mkdir(exist_ok=True)

        self.embedding_model = "models/embedding-001"
        self.dimension = 768  # Gemini embedding dimension

        # FAISS index and metadata
        self.index = None
        self.chunks = []  # Store chunk metadata
        self.chunk_embeddings = []

        self._load_or_create_index()

    def _load_or_create_index(self):
        """Load existing FAISS index or create a new one."""
        index_file = self.index_path / "faiss.index"
        metadata_file = self.index_path / "metadata.pkl"

        if index_file.exists() and metadata_file.exists() and FAISS_AVAILABLE:
            try:
                self.index = faiss.read_index(str(index_file))
                with open(metadata_file, 'rb') as f:
                    data = pickle.load(f)
                    self.chunks = data['chunks']
                    self.chunk_embeddings = data['embeddings']
                print(f"Loaded existing index with {len(self.chunks)} chunks")
            except Exception as e:
                print(f"Error loading index: {e}. Creating new index.")
                self._create_new_index()
        else:
            self._create_new_index()

    def _create_new_index(self):
        """Create a new FAISS index."""
        if FAISS_AVAILABLE:
            # Use IndexFlatL2 for exact search (can be upgraded to IndexIVFFlat for larger datasets)
            self.index = faiss.IndexFlatL2(self.dimension)
            print("Created new FAISS index")
        else:
            print("FAISS not available - using simple list-based search")
        self.chunks = []
        self.chunk_embeddings = []

    def generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Generate embedding for a text using Gemini.

        Args:
            text: Text to embed

        Returns:
            Numpy array of embedding or None on error
        """
        if not self.api_key:
            print("Warning: No API key provided. Cannot generate embeddings.")
            return None

        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            embedding = np.array(result['embedding'], dtype='float32')
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None

    def generate_query_embedding(self, query: str) -> Optional[np.ndarray]:
        """
        Generate embedding for a search query.

        Args:
            query: Query text

        Returns:
            Numpy array of embedding or None on error
        """
        if not self.api_key:
            return None

        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=query,
                task_type="retrieval_query"
            )
            embedding = np.array(result['embedding'], dtype='float32')
            return embedding
        except Exception as e:
            print(f"Error generating query embedding: {e}")
            return None

    def add_chunk(self, chunk: Dict[str, Any], file_path: str, language: str) -> bool:
        """
        Add a code chunk to the index.

        Args:
            chunk: Chunk dictionary with code and metadata
            file_path: Path to source file
            language: Programming language

        Returns:
            True if successful, False otherwise
        """
        # Create a text representation of the chunk for embedding
        chunk_text = self._create_chunk_text(chunk, file_path, language)

        # Generate embedding
        embedding = self.generate_embedding(chunk_text)
        if embedding is None:
            return False

        # Store metadata
        chunk_metadata = {
            'file_path': file_path,
            'language': language,
            'chunk_type': chunk.get('type', 'unknown'),
            'name': chunk.get('name'),
            'start_line': chunk.get('start_line'),
            'end_line': chunk.get('end_line'),
            'code': chunk.get('code', '')[:500],  # Store first 500 chars for reference
            'full_code': chunk.get('code', ''),
        }

        self.chunks.append(chunk_metadata)
        self.chunk_embeddings.append(embedding)

        # Add to FAISS index
        if FAISS_AVAILABLE and self.index is not None:
            self.index.add(embedding.reshape(1, -1))

        return True

    def _create_chunk_text(self, chunk: Dict, file_path: str, language: str) -> str:
        """
        Create a text representation of a chunk for embedding.

        Args:
            chunk: Chunk dictionary
            file_path: Source file path
            language: Programming language

        Returns:
            Text representation
        """
        parts = [f"Language: {language}"]

        if chunk.get('name'):
            parts.append(f"Name: {chunk['name']}")

        parts.append(f"Type: {chunk.get('type', 'unknown')}")
        parts.append(f"File: {Path(file_path).name}")

        # Add the actual code
        code = chunk.get('code', '')
        if code:
            parts.append(f"Code:\n{code}")

        return "\n".join(parts)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Search for relevant code chunks using semantic similarity.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of (chunk_metadata, similarity_score) tuples
        """
        if not self.chunks:
            return []

        query_embedding = self.generate_query_embedding(query)
        if query_embedding is None:
            # Fallback to simple keyword search
            return self._keyword_search(query, top_k)

        if FAISS_AVAILABLE and self.index is not None and self.index.ntotal > 0:
            # FAISS search
            top_k = min(top_k, self.index.ntotal)
            distances, indices = self.index.search(query_embedding.reshape(1, -1), top_k)

            results = []
            for idx, dist in zip(indices[0], distances[0]):
                if idx < len(self.chunks):
                    # Convert distance to similarity score (lower distance = higher similarity)
                    similarity = 1 / (1 + dist)
                    results.append((self.chunks[idx], float(similarity)))

            return results
        else:
            # Manual similarity computation
            return self._manual_search(query_embedding, top_k)

    def _manual_search(self, query_embedding: np.ndarray, top_k: int) -> List[Tuple[Dict, float]]:
        """Manual similarity search without FAISS."""
        if not self.chunk_embeddings:
            return []

        similarities = []
        for idx, chunk_emb in enumerate(self.chunk_embeddings):
            # Cosine similarity
            similarity = np.dot(query_embedding, chunk_emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(chunk_emb)
            )
            similarities.append((idx, float(similarity)))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        results = []
        for idx, sim in similarities[:top_k]:
            results.append((self.chunks[idx], sim))

        return results

    def _keyword_search(self, query: str, top_k: int) -> List[Tuple[Dict, float]]:
        """Fallback keyword-based search."""
        query_lower = query.lower()
        results = []

        for chunk in self.chunks:
            score = 0.0
            # Simple keyword matching
            if query_lower in chunk.get('full_code', '').lower():
                score += 1.0
            if chunk.get('name') and query_lower in chunk['name'].lower():
                score += 0.5
            if query_lower in chunk.get('file_path', '').lower():
                score += 0.3

            if score > 0:
                results.append((chunk, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def search_by_file(self, file_path: str) -> List[Dict]:
        """
        Get all chunks from a specific file.

        Args:
            file_path: Path to file

        Returns:
            List of chunk metadata
        """
        return [chunk for chunk in self.chunks if chunk['file_path'] == file_path]

    def search_by_language(self, language: str, limit: int = 100) -> List[Dict]:
        """
        Get chunks by programming language.

        Args:
            language: Programming language
            limit: Maximum number of results

        Returns:
            List of chunk metadata
        """
        results = [chunk for chunk in self.chunks if chunk['language'] == language]
        return results[:limit]

    def get_similar_chunks(self, file_path: str, chunk_name: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Find chunks similar to a specific chunk.

        Args:
            file_path: Source file path
            chunk_name: Name of the chunk
            top_k: Number of similar chunks to return

        Returns:
            List of (chunk_metadata, similarity_score) tuples
        """
        # Find the target chunk
        target_chunk = None
        for chunk in self.chunks:
            if chunk['file_path'] == file_path and chunk['name'] == chunk_name:
                target_chunk = chunk
                break

        if not target_chunk:
            return []

        # Use the chunk's code as query
        query = target_chunk.get('full_code', '')
        return self.search(query, top_k + 1)[1:]  # Exclude the chunk itself

    def save(self):
        """Persist the index and metadata to disk."""
        if FAISS_AVAILABLE and self.index is not None:
            index_file = self.index_path / "faiss.index"
            faiss.write_index(self.index, str(index_file))

        metadata_file = self.index_path / "metadata.pkl"
        with open(metadata_file, 'wb') as f:
            pickle.dump({
                'chunks': self.chunks,
                'embeddings': self.chunk_embeddings
            }, f)

        print(f"Saved index with {len(self.chunks)} chunks to {self.index_path}")

    def clear(self):
        """Clear all embeddings and recreate the index."""
        self._create_new_index()
        self.save()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the embedding index."""
        stats = {
            'total_chunks': len(self.chunks),
            'faiss_available': FAISS_AVAILABLE,
            'index_size': self.index.ntotal if FAISS_AVAILABLE and self.index else 0,
        }

        # Count by language
        languages = {}
        for chunk in self.chunks:
            lang = chunk.get('language', 'Unknown')
            languages[lang] = languages.get(lang, 0) + 1

        stats['languages'] = languages

        # Count by type
        types = {}
        for chunk in self.chunks:
            chunk_type = chunk.get('chunk_type', 'unknown')
            types[chunk_type] = types.get(chunk_type, 0) + 1

        stats['chunk_types'] = types

        return stats

    def __len__(self):
        return len(self.chunks)
