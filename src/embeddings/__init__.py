"""
Multi-vector embedding module.
Implements dense, sparse, and ColBERT embeddings for hybrid search.
"""

from .dense_embedder import DenseEmbedder
from .sparse_embedder import SparseEmbedder
from .colbert_embedder import ColBERTEmbedder
from .encoder_manager import EncoderManager

__all__ = [
    "DenseEmbedder",
    "SparseEmbedder",
    "ColBERTEmbedder",
    "EncoderManager",
]
