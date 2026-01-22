"""
Pydantic schemas for API requests and responses.
"""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Query request schema."""
    query: str = Field(..., description="User query")
    top_k: int = Field(10, description="Number of results to return", ge=1, le=50)
    filters: Optional[Dict] = Field(None, description="Optional filters")
    strategy: str = Field("adaptive", description="Search strategy: adaptive, rrf, or weighted")


class QueryResponse(BaseModel):
    """Query response schema."""
    answer: str = Field(..., description="Generated answer")
    query: str = Field(..., description="Original query")
    sources: List[str] = Field(..., description="Source citations")
    context: Optional[Dict] = Field(None, description="Retrieved context")
    model: Optional[str] = Field(None, description="Model used for generation")
    usage: Optional[Dict] = Field(None, description="Token usage statistics")


class IngestRequest(BaseModel):
    """Ingest request schema."""
    file_path: str = Field(..., description="Path to PDF file")
    ticker: Optional[str] = Field(None, description="Company ticker symbol")
    filing_date: Optional[str] = Field(None, description="Filing date (YYYY-MM-DD)")
    fiscal_year: Optional[int] = Field(None, description="Fiscal year")
    metadata: Optional[Dict] = Field(None, description="Additional metadata")


class IngestResponse(BaseModel):
    """Ingest response schema."""
    document_id: str = Field(..., description="Generated document ID")
    file_name: str = Field(..., description="Original file name")
    stats: Dict = Field(..., description="Ingestion statistics")
    message: str = Field(..., description="Status message")


class EntityResponse(BaseModel):
    """Entity response schema."""
    entities: List[Dict] = Field(..., description="List of entities")
    total: int = Field(..., description="Total number of entities")


class CompanyResponse(BaseModel):
    """Company overview response schema."""
    ticker: str = Field(..., description="Company ticker")
    name: str = Field(..., description="Company name")
    sector: Optional[str] = Field(None, description="Industry sector")
    metrics: List[Dict] = Field(default_factory=list, description="Financial metrics")
    executives: List[Dict] = Field(default_factory=list, description="Executive team")
    subsidiaries: List[str] = Field(default_factory=list, description="Subsidiaries")
