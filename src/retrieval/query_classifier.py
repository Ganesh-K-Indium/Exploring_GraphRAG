"""
Query classifier for adaptive search strategy.
Determines optimal weights for dense/sparse/colbert based on query type.
"""
from typing import Dict
from loguru import logger


class QueryClassifier:
    """
    Classifies queries to determine optimal search strategy.
    Analyzes query characteristics to assign weights to different search methods.
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize query classifier.
        
        Args:
            config: Configuration with strategy definitions
        """
        self.config = config or {}
        
        # Keyword indicators
        self.keyword_indicators = [
            "AAPL", "MSFT", "TSLA", "NVDA", "GOOGL", "AMZN",  # Tickers
            "10-K", "10-Q", "8-K",  # Filing types
            "EPS", "EBITDA", "GAAP",  # Financial acronyms
        ]
        
        # Semantic indicators
        self.semantic_words = [
            "what", "how", "why", "explain", "describe",
            "discuss", "summarize", "overview"
        ]
        
        # Analytical indicators
        self.analytical_words = [
            "compare", "analyze", "relationship", "trend",
            "between", "versus", "vs", "difference", "correlation"
        ]
        
        logger.info("QueryClassifier initialized")
    
    def classify(self, query: str) -> Dict[str, float]:
        """
        Classify query and determine search strategy.
        
        Args:
            query: Query text
        
        Returns:
            Dictionary with search weights and strategy
        """
        query_lower = query.lower()
        
        # Calculate indicator scores
        keyword_score = self._calculate_keyword_score(query, query_lower)
        semantic_score = self._calculate_semantic_score(query_lower)
        analytical_score = self._calculate_analytical_score(query_lower)
        
        # Normalize scores
        total = keyword_score + semantic_score + analytical_score
        if total == 0:
            total = 1.0
        
        sparse_weight = keyword_score / total
        dense_weight = semantic_score / total
        colbert_weight = analytical_score / total
        
        # Determine fusion method
        fusion_method = "weighted" if analytical_score > 0.3 else "rrf"
        
        # Determine query type
        query_type = self._determine_query_type(
            sparse_weight, dense_weight, colbert_weight
        )
        
        return {
            "sparse_weight": sparse_weight,
            "dense_weight": dense_weight,
            "colbert_weight": colbert_weight,
            "fusion_method": fusion_method,
            "query_type": query_type,
            "scores": {
                "keyword": keyword_score,
                "semantic": semantic_score,
                "analytical": analytical_score
            }
        }
    
    def _calculate_keyword_score(self, query: str, query_lower: str) -> float:
        """Calculate keyword matching importance."""
        score = 0.0
        
        # Check for tickers (uppercase)
        if any(ticker in query for ticker in self.keyword_indicators[:6]):
            score += 0.4
        
        # Check for filing types
        if any(filing in query for filing in ["10-K", "10-Q", "8-K"]):
            score += 0.3
        
        # Check for financial acronyms
        if any(acronym in query for acronym in self.keyword_indicators[9:]):
            score += 0.2
        
        # All caps words (likely acronyms/tickers)
        words = query.split()
        caps_words = [w for w in words if w.isupper() and len(w) > 1]
        if caps_words:
            score += 0.1 * min(len(caps_words), 3)
        
        # Exact phrases in quotes
        if '"' in query:
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_semantic_score(self, query_lower: str) -> float:
        """Calculate semantic understanding importance."""
        score = 0.0
        
        # Check for semantic keywords
        for word in self.semantic_words:
            if word in query_lower:
                score += 0.15
        
        # Long queries are usually semantic
        word_count = len(query_lower.split())
        if word_count > 8:
            score += 0.3
        elif word_count > 5:
            score += 0.15
        
        # Questions are semantic
        if "?" in query_lower:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_analytical_score(self, query_lower: str) -> float:
        """Calculate analytical/complex query importance."""
        score = 0.0
        
        # Check for analytical keywords
        for word in self.analytical_words:
            if word in query_lower:
                score += 0.2
        
        # Multiple entities suggest comparison
        # Simple heuristic: check for "and", multiple company indicators
        if " and " in query_lower or " , " in query_lower:
            score += 0.15
        
        # Complex sentence structure
        if query_lower.count(",") >= 2:
            score += 0.1
        
        return min(score, 1.0)
    
    def _determine_query_type(
        self,
        sparse_weight: float,
        dense_weight: float,
        colbert_weight: float
    ) -> str:
        """Determine overall query type."""
        if sparse_weight > 0.5:
            return "keyword_heavy"
        elif dense_weight > 0.5:
            return "semantic_heavy"
        elif colbert_weight > 0.4:
            return "analytical_heavy"
        else:
            return "balanced"
    
    def get_content_boost(self, query: str) -> Dict[str, float]:
        """
        Determine content type boosting based on query.
        
        Args:
            query: Query text
        
        Returns:
            Dictionary with content type boost values
        """
        query_lower = query.lower()
        boosts = {
            "table": 0.0,
            "chart": 0.0,
            "text": 0.0
        }
        
        # Table indicators
        table_keywords = [
            "breakdown", "details", "by segment", "quarterly",
            "annual", "table", "data", "figures"
        ]
        if any(kw in query_lower for kw in table_keywords):
            boosts["table"] = 0.4
        
        # Chart indicators
        chart_keywords = [
            "trend", "over time", "growth", "chart", "graph",
            "visual", "show me"
        ]
        if any(kw in query_lower for kw in chart_keywords):
            boosts["chart"] = 0.3
        
        # Text/narrative indicators
        text_keywords = [
            "explain", "describe", "discuss", "narrative",
            "strategy", "overview"
        ]
        if any(kw in query_lower for kw in text_keywords):
            boosts["text"] = 0.2
        
        return boosts
