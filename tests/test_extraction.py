"""
Tests for PDF extraction modules.
"""
import pytest
from pathlib import Path
from src.extraction import PDFExtractor, TextProcessor, TableProcessor


@pytest.fixture
def extraction_config():
    """Sample extraction configuration."""
    return {
        "text": {
            "chunk_size": 512,
            "chunk_overlap": 64,
            "section_markers": ["ITEM 1.", "ITEM 7."]
        },
        "tables": {
            "min_rows": 2,
            "min_cols": 2
        },
        "images": {
            "min_size_kb": 50,
            "extract_charts": False  # Disable for testing
        }
    }


def test_text_processor_init(extraction_config):
    """Test TextProcessor initialization."""
    processor = TextProcessor(extraction_config["text"])
    assert processor.chunk_size == 512
    assert processor.chunk_overlap == 64


def test_text_chunking(extraction_config):
    """Test text chunking."""
    processor = TextProcessor(extraction_config["text"])
    
    text = "This is a test. " * 100  # Long text
    chunks = processor.chunk_text(text)
    
    assert len(chunks) > 0
    assert all("text" in chunk for chunk in chunks)


def test_table_processor_init(extraction_config):
    """Test TableProcessor initialization."""
    processor = TableProcessor(extraction_config["tables"])
    assert processor.min_rows == 2
    assert processor.min_cols == 2


@pytest.mark.skipif(
    not Path("tests/fixtures/sample.pdf").exists(),
    reason="Sample PDF not available"
)
def test_pdf_extraction(extraction_config):
    """Test full PDF extraction."""
    extractor = PDFExtractor(
        config=extraction_config,
        use_vision=False
    )
    
    result = extractor.extract_from_pdf(
        "tests/fixtures/sample.pdf",
        metadata={"ticker": "TEST"}
    )
    
    assert "document_id" in result
    assert "chunks" in result
    assert len(result["chunks"]) > 0
