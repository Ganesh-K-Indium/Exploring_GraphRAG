"""
Tests for embedding modules.
"""
import pytest
import numpy as np
from src.embeddings import DenseEmbedder, SparseEmbedder, EncoderManager


@pytest.fixture
def sample_text():
    """Sample text for embedding."""
    return "Apple Inc. reported revenue of $394.3 billion for fiscal year 2024."


def test_dense_embedder_init():
    """Test DenseEmbedder initialization."""
    config = {
        "model": "sentence-transformers/all-mpnet-base-v2",
        "dimension": 768,
        "cache_enabled": False
    }
    
    embedder = DenseEmbedder(config)
    assert embedder.dimension == 768


def test_dense_embedding(sample_text):
    """Test dense embedding generation."""
    config = {
        "model": "sentence-transformers/all-mpnet-base-v2",
        "cache_enabled": False
    }
    
    embedder = DenseEmbedder(config)
    embedding = embedder.encode(sample_text)
    
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)


def test_sparse_embedder_init():
    """Test SparseEmbedder initialization."""
    config = {
        "model": "naver/splade-cocondenser-ensembledistil",
        "device": "cpu"
    }
    
    embedder = SparseEmbedder(config)
    assert embedder.device == "cpu"


def test_sparse_embedding(sample_text):
    """Test sparse embedding generation."""
    config = {
        "model": "naver/splade-cocondenser-ensembledistil",
        "device": "cpu"
    }
    
    embedder = SparseEmbedder(config)
    embedding = embedder.encode(sample_text)
    
    assert isinstance(embedding, dict)
    assert "indices" in embedding
    assert "values" in embedding


@pytest.mark.slow
def test_encoder_manager(sample_text):
    """Test EncoderManager with all encoders."""
    config = {
        "dense": {
            "model": "sentence-transformers/all-mpnet-base-v2",
            "cache_enabled": False
        },
        "sparse": {
            "model": "naver/splade-cocondenser-ensembledistil",
            "device": "cpu"
        },
        "colbert": {
            "model": "bert-base-uncased"
        }
    }
    
    manager = EncoderManager(config)
    result = manager.encode_all(sample_text)
    
    assert "dense" in result
    assert "sparse" in result
    assert "colbert" in result
