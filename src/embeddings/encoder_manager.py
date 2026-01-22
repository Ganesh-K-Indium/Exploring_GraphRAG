"""
Encoder manager for orchestrating multi-vector embeddings.
Handles parallel encoding with all three methods.
"""
from typing import Dict, List, Union
from concurrent.futures import ThreadPoolExecutor
from loguru import logger

from .dense_embedder import DenseEmbedder
from .sparse_embedder import SparseEmbedder
from .colbert_embedder import ColBERTEmbedder


class EncoderManager:
    """
    Manages multiple embedding encoders.
    Provides unified interface for multi-vector encoding.
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize encoder manager.
        
        Args:
            config: Configuration for all encoders
        """
        self.config = config or {}
        
        # Initialize encoders
        logger.info("Initializing encoders...")
        
        dense_config = self.config.get("dense", {})
        sparse_config = self.config.get("sparse", {})
        colbert_config = self.config.get("colbert", {})
        
        self.dense_encoder = DenseEmbedder(dense_config)
        self.sparse_encoder = SparseEmbedder(sparse_config)
        self.colbert_encoder = ColBERTEmbedder(colbert_config)
        
        logger.info("EncoderManager initialized with all three encoders")
    
    def encode_all(
        self,
        text: str,
        input_type: str = "document"
    ) -> Dict:
        """
        Encode text with all three methods in parallel.
        
        Args:
            text: Input text
            input_type: "document" or "query"
        
        Returns:
            Dictionary with all three embedding types
        """
        results = {}
        
        # Execute in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit tasks
            dense_future = executor.submit(
                self.dense_encoder.encode,
                text,
                input_type
            )
            sparse_future = executor.submit(
                self.sparse_encoder.encode,
                text
            )
            
            # ColBERT needs different method based on type
            if input_type == "query":
                colbert_future = executor.submit(
                    self.colbert_encoder.encode_query,
                    text
                )
            else:
                colbert_future = executor.submit(
                    self.colbert_encoder.encode_passage,
                    text
                )
            
            # Collect results
            results["dense"] = dense_future.result()
            results["sparse"] = sparse_future.result()
            results["colbert"] = colbert_future.result()
        
        return results
    
    def encode_batch(
        self,
        texts: List[str],
        input_type: str = "document",
        batch_size: int = 32
    ) -> List[Dict]:
        """
        Encode multiple texts efficiently.
        
        Args:
            texts: List of texts
            input_type: "document" or "query"
            batch_size: Batch size for encoding
        
        Returns:
            List of dictionaries with embeddings
        """
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Encode batch with each encoder
            dense_embs = self.dense_encoder.encode(batch, input_type)
            sparse_embs = self.sparse_encoder.encode(batch)
            
            if input_type == "query":
                colbert_embs = self.colbert_encoder.encode_query(batch)
            else:
                colbert_embs = self.colbert_encoder.encode_passage(batch)
            
            # Combine results
            for j, text in enumerate(batch):
                results.append({
                    "text": text,
                    "dense": dense_embs[j],
                    "sparse": sparse_embs[j],
                    "colbert": colbert_embs[j]
                })
        
        return results
    
    def encode_documents(self, texts: List[str]) -> List[Dict]:
        """Encode documents (convenience method)."""
        return self.encode_batch(texts, input_type="document")
    
    def encode_queries(self, queries: List[str]) -> List[Dict]:
        """Encode queries (convenience method)."""
        return self.encode_batch(queries, input_type="query")
    
    def get_dense_dim(self) -> int:
        """Get dense embedding dimension."""
        return self.dense_encoder.dimension
    
    def get_colbert_dim(self) -> int:
        """Get ColBERT embedding dimension."""
        return self.colbert_encoder.dimension
