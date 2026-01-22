"""
Pytest configuration and fixtures.
"""
import pytest


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


@pytest.fixture(scope="session")
def sample_metadata():
    """Sample 10-K metadata."""
    return {
        "ticker": "AAPL",
        "filing_date": "2024-10-31",
        "fiscal_year": 2024,
        "company_name": "Apple Inc.",
        "sector": "Technology"
    }


@pytest.fixture(scope="session")
def sample_chunk():
    """Sample text chunk."""
    return {
        "chunk_id": "test_chunk_1",
        "chunk_type": "text",
        "text_content": "Apple Inc. reported strong financial results for Q4 2024.",
        "metadata": {
            "section": "Item_7_MD&A",
            "page_numbers": [45],
            "company_ticker": "AAPL",
            "fiscal_year": 2024
        }
    }
