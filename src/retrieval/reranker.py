"""
Result reranking with multi-factor scoring.
Combines relevance, recency, and graph centrality.
"""
from typing import List, Dict
from loguru import logger
import math


class Reranker:
    """
    Reranks search results using multiple factors.
    Combines vector similarity, graph centrality, and temporal relevance.
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize reranker.
        
        Args:
            config: Reranking configuration
        """
        self.config = config or {}
        
        # Weights for different factors
        self.similarity_weight = self.config.get("similarity_weight", 0.6)
        self.graph_weight = self.config.get("graph_weight", 0.2)
        self.temporal_weight = self.config.get("temporal_weight", 0.2)
        
        logger.info("Reranker initialized")
    
    def rerank(
        self,
        results: List[Dict],
        graph_context: Dict = None,
        current_year: int = 2024
    ) -> List[Dict]:
        """
        Rerank results with multi-factor scoring.
        
        Args:
            results: Search results
            graph_context: Optional graph context
            current_year: Current year for recency scoring
        
        Returns:
            Reranked results
        """
        if not results:
            return results
        
        # Calculate additional scores
        for result in results:
            payload = result.get("payload", {})
            
            # Base similarity score (already present)
            similarity_score = result.get("score", 0.0)
            
            # Graph centrality score
            graph_score = self._calculate_graph_score(
                result,
                graph_context
            )
            
            # Temporal relevance score
            temporal_score = self._calculate_temporal_score(
                payload,
                current_year
            )
            
            # Combined score
            combined_score = (
                similarity_score * self.similarity_weight +
                graph_score * self.graph_weight +
                temporal_score * self.temporal_weight
            )
            
            result["rerank_score"] = combined_score
            result["score_breakdown"] = {
                "similarity": similarity_score,
                "graph": graph_score,
                "temporal": temporal_score
            }
        
        # Sort by rerank score
        results.sort(key=lambda x: x["rerank_score"], reverse=True)
        
        return results
    
    def _calculate_graph_score(
        self,
        result: Dict,
        graph_context: Dict
    ) -> float:
        """
        Calculate graph centrality score.
        
        Higher score for results with more graph connections.
        """
        if not graph_context:
            return 0.5  # Neutral score
        
        payload = result.get("payload", {})
        neo4j_ids = payload.get("neo4j_node_ids", [])
        
        if not neo4j_ids:
            return 0.3  # Low score for unlinked results
        
        # Count relationships in graph context
        relationships = graph_context.get("relationships", [])
        
        # Score based on number of relationships
        rel_count = sum(
            1 for rel in relationships
            if any(node_id in str(rel) for node_id in neo4j_ids)
        )
        
        # Normalize to 0-1 range
        max_rels = 10  # Assume max 10 relationships
        score = min(rel_count / max_rels, 1.0)
        
        return score
    
    def _calculate_temporal_score(
        self,
        payload: Dict,
        current_year: int
    ) -> float:
        """
        Calculate temporal relevance score.
        
        More recent filings get higher scores.
        """
        fiscal_year = payload.get("fiscal_year")
        
        if not fiscal_year:
            return 0.5  # Neutral score
        
        try:
            fiscal_year = int(fiscal_year)
        except (ValueError, TypeError):
            return 0.5
        
        # Calculate age
        age = current_year - fiscal_year
        
        # Exponential decay
        # Recent = 1.0, 5 years old = ~0.6
        score = math.exp(-0.1 * age)
        
        return max(min(score, 1.0), 0.0)
    
    def diversify_results(
        self,
        results: List[Dict],
        diversity_factor: float = 0.3
    ) -> List[Dict]:
        """
        Diversify results to avoid redundancy.
        
        Args:
            results: Search results
            diversity_factor: How much to prioritize diversity (0-1)
        
        Returns:
            Diversified results
        """
        if len(results) <= 1:
            return results
        
        diversified = [results[0]]  # Always include top result
        
        for result in results[1:]:
            # Calculate similarity to already selected results
            avg_similarity = self._average_similarity_to_selected(
                result,
                diversified
            )
            
            # Adjust score based on similarity
            diversity_penalty = avg_similarity * diversity_factor
            result["diversity_score"] = result["rerank_score"] * (1 - diversity_penalty)
            
            diversified.append(result)
        
        # Re-sort by diversity score
        diversified.sort(key=lambda x: x.get("diversity_score", x["rerank_score"]), reverse=True)
        
        return diversified
    
    def _average_similarity_to_selected(
        self,
        result: Dict,
        selected: List[Dict]
    ) -> float:
        """Calculate average content similarity to selected results."""
        if not selected:
            return 0.0
        
        payload = result.get("payload", {})
        result_entities = set(payload.get("entities", []))
        result_section = payload.get("section", "")
        
        similarities = []
        
        for sel in selected:
            sel_payload = sel.get("payload", {})
            sel_entities = set(sel_payload.get("entities", []))
            sel_section = sel_payload.get("section", "")
            
            # Entity overlap
            if result_entities and sel_entities:
                entity_sim = len(result_entities & sel_entities) / len(result_entities | sel_entities)
            else:
                entity_sim = 0.0
            
            # Section similarity
            section_sim = 1.0 if result_section == sel_section else 0.0
            
            # Combined similarity
            similarities.append((entity_sim + section_sim) / 2)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
