"""
TechDocAgent Advanced - Next-generation technical documentation agent with memory, embeddings, and incremental updates.

This package implements the advanced features outlined in TechDocAgent_AdvancedRoadmap.md:
- Memory & contextual awareness
- Multi-doc & multi-format support
- Advanced code understanding with AST
- Embeddings and vector search
- Change detection and incremental updates
- Feedback loop system
"""

__version__ = "2.0.0"
__author__ = "TechDocAgent Team"

from .agent import TechDocAgent
from .memory import MemoryManager
from .embeddings import EmbeddingManager
from .change_detector import ChangeDetector

__all__ = [
    'TechDocAgent',
    'MemoryManager',
    'EmbeddingManager',
    'ChangeDetector',
]
