"""
FastAPI server module.
REST API for the Graph RAG system.
"""

from .server import app
from .schemas import QueryRequest, QueryResponse, IngestRequest, IngestResponse

__all__ = [
    "app",
    "QueryRequest",
    "QueryResponse",
    "IngestRequest",
    "IngestResponse",
]
