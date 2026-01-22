"""
Sparse embedding using SPLADE.
Keyword-based embeddings for exact term matching.
"""
from typing import List, Dict, Union
import torch
from loguru import logger
from transformers import AutoModelForMaskedLM, AutoTokenizer

from src.config import settings


class SparseEmbedder:
    """
    Sparse embedding encoder using SPLADE.
    Creates sparse vector representations for keyword matching.
    """
    
    def __init__(self, config: dict = None):
        """
        Initialize sparse embedder.
        
        Args:
            config: Embedding configuration
        """
        self.config = config or {}
        self.model_name = self.config.get("model", settings.sparse_embedding_model)
        self.max_length = self.config.get("max_length", 512)
        self.device = self.config.get("device", "cpu")
        
        logger.info(f"Loading SPLADE model: {self.model_name}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForMaskedLM.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            logger.error(f"Failed to load SPLADE model: {e}")
            raise
        
        logger.info("SparseEmbedder initialized")
    
    def encode(
        self,
        texts: Union[str, List[str]]
    ) -> Union[Dict, List[Dict]]:
        """
        Encode text(s) to sparse embeddings.
        
        Args:
            texts: Single text or list of texts
        
        Returns:
            Sparse vector(s) as dict with "indices" and "values"
        """
        single_input = isinstance(texts, str)
        if single_input:
            texts = [texts]
        
        sparse_vectors = []
        
        with torch.no_grad():
            for text in texts:
                sparse_vec = self._encode_single(text)
                sparse_vectors.append(sparse_vec)
        
        return sparse_vectors[0] if single_input else sparse_vectors
    
    def _encode_single(self, text: str) -> Dict:
        """Encode single text to sparse vector."""
        # Tokenize
        tokens = self.tokenizer(
            text,
            max_length=self.max_length,
            padding=True,
            truncation=True,
            return_tensors="pt"
        ).to(self.device)
        
        # Forward pass
        output = self.model(**tokens)
        logits = output.logits
        
        # SPLADE scoring
        # Apply log(1 + ReLU(x)) transformation
        relu_log = torch.log1p(torch.relu(logits))
        
        # Weight by attention mask
        weighted_log = relu_log * tokens["attention_mask"].unsqueeze(-1)
        
        # Max pooling over tokens
        max_val, _ = torch.max(weighted_log, dim=1)
        
        # Convert to sparse format
        sparse_vector = self._to_sparse_dict(max_val[0])
        
        return sparse_vector
    
    def _to_sparse_dict(self, vector: torch.Tensor) -> Dict:
        """
        Convert dense tensor to sparse dictionary.
        
        Args:
            vector: Dense vector tensor
        
        Returns:
            Dictionary with "indices" and "values"
        """
        # Get non-zero elements
        non_zero_mask = vector > 0
        indices = torch.nonzero(non_zero_mask).squeeze().tolist()
        values = vector[non_zero_mask].tolist()
        
        # Handle single index case
        if isinstance(indices, int):
            indices = [indices]
            values = [values] if isinstance(values, float) else values
        
        return {
            "indices": indices,
            "values": values
        }
    
    def batch_encode(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[Dict]:
        """
        Encode texts in batches for efficiency.
        
        Args:
            texts: List of texts
            batch_size: Batch size
        
        Returns:
            List of sparse vectors
        """
        sparse_vectors = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_vectors = self.encode(batch)
            sparse_vectors.extend(batch_vectors)
        
        return sparse_vectors
