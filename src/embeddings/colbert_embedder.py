"""
ColBERT late interaction embeddings.
Token-level embeddings for fine-grained matching.
"""
from typing import List, Union
import torch
from loguru import logger
from transformers import AutoModel, AutoTokenizer
import numpy as np

from src.config import settings


class ColBERTEmbedder:
    """
    ColBERT encoder for late interaction.
    Creates token-level embeddings for precise matching.
    
    Note: This is a simplified implementation. For production,
    consider using the official ColBERT library.
    """
    
    def __init__(self, config: dict = None):
        """
        Initialize ColBERT embedder.
        
        Args:
            config: Embedding configuration
        """
        self.config = config or {}
        self.model_name = self.config.get("model", "bert-base-uncased")
        self.dimension = self.config.get("dimension", 128)
        self.doc_maxlen = self.config.get("doc_maxlen", 300)
        self.query_maxlen = self.config.get("query_maxlen", 32)
        self.device = "cpu"  # ColBERT is compute-intensive
        
        logger.info(f"Loading ColBERT model: {self.model_name}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            
            # Linear layer for dimension reduction
            model_dim = self.model.config.hidden_size
            self.linear = torch.nn.Linear(model_dim, self.dimension)
            self.linear.to(self.device)
        except Exception as e:
            logger.error(f"Failed to load ColBERT model: {e}")
            raise
        
        logger.info("ColBERTEmbedder initialized")
    
    def encode_query(
        self,
        queries: Union[str, List[str]]
    ) -> Union[np.ndarray, List[np.ndarray]]:
        """
        Encode query with special handling.
        
        Args:
            queries: Single query or list of queries
        
        Returns:
            Token embeddings (num_tokens, dimension)
        """
        single_input = isinstance(queries, str)
        if single_input:
            queries = [queries]
        
        embeddings = []
        
        with torch.no_grad():
            for query in queries:
                emb = self._encode_text(query, self.query_maxlen, is_query=True)
                embeddings.append(emb)
        
        return embeddings[0] if single_input else embeddings
    
    def encode_passage(
        self,
        passages: Union[str, List[str]]
    ) -> Union[np.ndarray, List[np.ndarray]]:
        """
        Encode document passage.
        
        Args:
            passages: Single passage or list of passages
        
        Returns:
            Token embeddings (num_tokens, dimension)
        """
        single_input = isinstance(passages, str)
        if single_input:
            passages = [passages]
        
        embeddings = []
        
        with torch.no_grad():
            for passage in passages:
                emb = self._encode_text(passage, self.doc_maxlen, is_query=False)
                embeddings.append(emb)
        
        return embeddings[0] if single_input else embeddings
    
    def _encode_text(
        self,
        text: str,
        max_length: int,
        is_query: bool
    ) -> np.ndarray:
        """Encode text to token embeddings."""
        # Tokenize
        tokens = self.tokenizer(
            text,
            max_length=max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        ).to(self.device)
        
        # Get embeddings
        outputs = self.model(**tokens)
        embeddings = outputs.last_hidden_state[0]  # (seq_len, hidden_dim)
        
        # Reduce dimension
        embeddings = self.linear(embeddings)  # (seq_len, dimension)
        
        # L2 normalize
        embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=-1)
        
        # Filter padding tokens
        mask = tokens["attention_mask"][0].bool()
        embeddings = embeddings[mask]
        
        return embeddings.cpu().numpy()
    
    def compute_maxsim(
        self,
        query_embeddings: np.ndarray,
        doc_embeddings: np.ndarray
    ) -> float:
        """
        Compute MaxSim score between query and document.
        
        For each query token, find max similarity with any doc token.
        Sum these max similarities.
        
        Args:
            query_embeddings: Query token embeddings (num_query_tokens, dim)
            doc_embeddings: Document token embeddings (num_doc_tokens, dim)
        
        Returns:
            MaxSim score
        """
        # Compute all pairwise similarities
        similarities = np.dot(query_embeddings, doc_embeddings.T)
        
        # For each query token, take max similarity
        max_sims = np.max(similarities, axis=1)
        
        # Sum over query tokens
        score = np.sum(max_sims)
        
        return float(score)
    
    def batch_encode_passages(
        self,
        passages: List[str],
        batch_size: int = 16
    ) -> List[np.ndarray]:
        """Batch encode passages for efficiency."""
        embeddings = []
        
        for i in range(0, len(passages), batch_size):
            batch = passages[i:i + batch_size]
            batch_embs = self.encode_passage(batch)
            embeddings.extend(batch_embs)
        
        return embeddings
