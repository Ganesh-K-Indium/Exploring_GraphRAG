"""
Tests for retrieval modules.
"""
import pytest
from src.retrieval import QueryClassifier, Reranker


@pytest.fixture
def query_classifier():
    """Query classifier fixture."""
    return QueryClassifier()


def test_query_classifier_keyword_query(query_classifier):
    """Test classification of keyword-heavy query."""
    query = "Find AAPL 10-K EPS data"
    
    result = query_classifier.classify(query)
    
    assert result["query_type"] in ["keyword_heavy", "balanced"]
    assert result["sparse_weight"] > 0.3


def test_query_classifier_semantic_query(query_classifier):
    """Test classification of semantic query."""
    query = "What are the main business risks facing technology companies?"
    
    result = query_classifier.classify(query)
    
    assert result["query_type"] in ["semantic_heavy", "balanced"]
    assert result["dense_weight"] > 0.3


def test_query_classifier_analytical_query(query_classifier):
    """Test classification of analytical query."""
    query = "Compare the revenue growth trends between Apple and Microsoft"
    
    result = query_classifier.classify(query)
    
    assert result["query_type"] in ["analytical_heavy", "balanced"]
    assert result["colbert_weight"] > 0.2


def test_content_boost(query_classifier):
    """Test content type boosting."""
    query = "Show me the revenue breakdown table"
    
    boosts = query_classifier.get_content_boost(query)
    
    assert boosts["table"] > 0.0
    assert "table" in query.lower()


def test_reranker():
    """Test result reranking."""
    reranker = Reranker()
    
    results = [
        {
            "id": 1,
            "score": 0.8,
            "payload": {"fiscal_year": 2024, "neo4j_node_ids": ["1", "2"]}
        },
        {
            "id": 2,
            "score": 0.7,
            "payload": {"fiscal_year": 2020, "neo4j_node_ids": []}
        }
    ]
    
    graph_context = {
        "entities": [],
        "relationships": [{"rel": "test"}]
    }
    
    reranked = reranker.rerank(results, graph_context, current_year=2024)
    
    assert len(reranked) == 2
    assert all("rerank_score" in r for r in reranked)
    # More recent document should rank higher (all else being equal)
    assert reranked[0]["payload"]["fiscal_year"] >= reranked[1]["payload"]["fiscal_year"]
