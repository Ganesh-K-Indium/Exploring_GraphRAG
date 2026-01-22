"""
Hybrid retrieval with multi-vector fusion.
Combines dense, sparse, and ColBERT search with adaptive weights.
"""
from typing import List, Dict, Optional
from loguru import logger
import numpy as np

from src.databases.qdrant_manager import QdrantManager
from src.embeddings.encoder_manager import EncoderManager
from src.embeddings.colbert_embedder import ColBERTEmbedder
from .query_classifier import QueryClassifier


class HybridRetriever:
    """
    Hybrid retriever combining multiple search methods.
    Implements RRF and weighted fusion strategies.
    """
    
    def __init__(
        self,
        qdrant_manager: QdrantManager,
        encoder_manager: EncoderManager,
        config: Dict = None
    ):
        """
        Initialize hybrid retriever.
        
        Args:
            qdrant_manager: Qdrant database manager
            encoder_manager: Multi-encoder manager
            config: Retrieval configuration
        """
        self.qdrant = qdrant_manager
        self.encoders = encoder_manager
        self.config = config or {}
        
        self.query_classifier = QueryClassifier(config)
        self.rrf_k = config.get("rrf_k", 60)
        
        logger.info("HybridRetriever initialized")
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict] = None,
        strategy: str = "adaptive"
    ) -> List[Dict]:
        """
        Perform hybrid search.
        
        Args:
            query: Query text
            top_k: Number of results
            filters: Optional Qdrant filters
            strategy: "adaptive", "rrf", or "weighted"
        
        Returns:
            Search results
        """
        logger.info(f"Hybrid search: '{query}' (top_k={top_k})")
        
        # Classify query
        query_strategy = self.query_classifier.classify(query)
        logger.info(f"Query type: {query_strategy['query_type']}")
        
        # Encode query with all methods
        query_embeddings = self.encoders.encode_all(query, input_type="query")
        
        # Perform searches
        results = self._multi_search(
            query_embeddings,
            top_k * 3,  # Get more for fusion
            filters
        )
        
        # Apply fusion
        if strategy == "adaptive":
            fusion_method = query_strategy["fusion_method"]
        else:
            fusion_method = strategy
        
        if fusion_method == "rrf":
            final_results = self._reciprocal_rank_fusion(
                results["dense"],
                results["sparse"],
                results["colbert"],
                top_k
            )
        else:  # weighted
            weights = [
                query_strategy["dense_weight"],
                query_strategy["sparse_weight"],
                query_strategy["colbert_weight"]
            ]
            final_results = self._weighted_fusion(
                results["dense"],
                results["sparse"],
                results["colbert"],
                weights,
                top_k
            )
        
        # Apply content boosting
        content_boosts = self.query_classifier.get_content_boost(query)
        final_results = self._apply_content_boost(final_results, content_boosts)
        
        return final_results[:top_k]
    
    def _multi_search(
        self,
        query_embeddings: Dict,
        limit: int,
        filters: Optional[Dict]
    ) -> Dict[str, List[Dict]]:
        """Perform searches with all three methods."""
        # Dense search
        dense_results = self.qdrant.search_dense(
            query_embeddings["dense"],
            limit=limit,
            filters=filters
        )
        
        # Sparse search
        sparse_results = self.qdrant.search_sparse(
            query_embeddings["sparse"],
            limit=limit,
            filters=filters
        )
        
        # ColBERT search (simulated with dense + rescoring)
        colbert_results = self._colbert_search(
            query_embeddings["colbert"],
            limit,
            filters
        )
        
        return {
            "dense": dense_results,
            "sparse": sparse_results,
            "colbert": colbert_results
        }
    
    def _colbert_search(
        self,
        query_embeddings: np.ndarray,
        limit: int,
        filters: Optional[Dict]
    ) -> List[Dict]:
        """
        ColBERT late interaction search.
        
        First stage: Dense retrieval for candidates
        Second stage: ColBERT MaxSim scoring
        """
        # Get mean of query tokens for first-stage retrieval
        query_dense = query_embeddings.mean(axis=0).tolist()
        
        # First stage: dense retrieval
        candidates = self.qdrant.search_dense(
            query_dense,
            limit=limit * 2,
            filters=filters
        )
        
        # Second stage: ColBERT scoring
        scored_results = []
        
        for candidate in candidates:
            payload = candidate.get("payload", {})
            doc_colbert = payload.get("colbert_tokens")
            
            if doc_colbert:
                doc_embeddings = np.array(doc_colbert)
                
                # Compute MaxSim score
                maxsim_score = self._compute_maxsim(
                    query_embeddings,
                    doc_embeddings
                )
                
                candidate["score"] = maxsim_score
                scored_results.append(candidate)
        
        # Sort by ColBERT score
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        
        return scored_results[:limit]
    
    def _compute_maxsim(
        self,
        query_tokens: np.ndarray,
        doc_tokens: np.ndarray
    ) -> float:
        """Compute ColBERT MaxSim score."""
        # Compute all pairwise similarities
        similarities = np.dot(query_tokens, doc_tokens.T)
        
        # For each query token, take max similarity
        max_sims = np.max(similarities, axis=1)
        
        # Sum over query tokens
        return float(np.sum(max_sims))
    
    def _reciprocal_rank_fusion(
        self,
        dense_results: List[Dict],
        sparse_results: List[Dict],
        colbert_results: List[Dict],
        top_k: int
    ) -> List[Dict]:
        """
        Reciprocal Rank Fusion.
        
        Formula: score = sum(1 / (k + rank_i))
        """
        scores = {}
        
        # Process each result list
        for results in [dense_results, sparse_results, colbert_results]:
            for rank, result in enumerate(results, start=1):
                point_id = result["id"]
                rrf_score = 1.0 / (self.rrf_k + rank)
                
                if point_id not in scores:
                    scores[point_id] = {
                        "score": 0.0,
                        "payload": result.get("payload", {})
                    }
                scores[point_id]["score"] += rrf_score
        
        # Sort by combined score
        sorted_results = sorted(
            scores.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        return [
            {
                "id": point_id,
                "score": data["score"],
                "payload": data["payload"]
            }
            for point_id, data in sorted_results[:top_k]
        ]
    
    def _weighted_fusion(
        self,
        dense_results: List[Dict],
        sparse_results: List[Dict],
        colbert_results: List[Dict],
        weights: List[float],
        top_k: int
    ) -> List[Dict]:
        """Weighted combination of search results."""
        # Normalize scores for each result list
        def normalize_scores(results):
            if not results:
                return []
            
            scores = [r["score"] for r in results]
            max_score = max(scores) if scores else 1.0
            min_score = min(scores) if scores else 0.0
            score_range = max_score - min_score or 1.0
            
            normalized = []
            for r in results:
                norm_score = (r["score"] - min_score) / score_range
                normalized.append((r["id"], norm_score, r.get("payload", {})))
            
            return normalized
        
        dense_norm = normalize_scores(dense_results)
        sparse_norm = normalize_scores(sparse_results)
        colbert_norm = normalize_scores(colbert_results)
        
        # Combine with weights
        combined_scores = {}
        
        for result_list, weight in zip(
            [dense_norm, sparse_norm, colbert_norm],
            weights
        ):
            for point_id, score, payload in result_list:
                if point_id not in combined_scores:
                    combined_scores[point_id] = {
                        "score": 0.0,
                        "payload": payload
                    }
                combined_scores[point_id]["score"] += score * weight
        
        # Sort by combined score
        sorted_results = sorted(
            combined_scores.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        return [
            {
                "id": point_id,
                "score": data["score"],
                "payload": data["payload"]
            }
            for point_id, data in sorted_results[:top_k]
        ]
    
    def _apply_content_boost(
        self,
        results: List[Dict],
        boosts: Dict[str, float]
    ) -> List[Dict]:
        """Apply content type boosting to results."""
        for result in results:
            payload = result.get("payload", {})
            
            # Check content type and apply boost
            if payload.get("has_table") and boosts["table"] > 0:
                result["score"] *= (1 + boosts["table"])
            
            if payload.get("has_chart") and boosts["chart"] > 0:
                result["score"] *= (1 + boosts["chart"])
            
            chunk_type = payload.get("chunk_type", "text")
            if chunk_type == "text" and boosts["text"] > 0:
                result["score"] *= (1 + boosts["text"])
        
        # Re-sort after boosting
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results
