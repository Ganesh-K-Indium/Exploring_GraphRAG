"""
FastAPI server for Graph RAG system.
Provides REST API endpoints for ingestion and querying.
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.config import settings, load_yaml_config
from src.databases import Neo4jManager, QdrantManager
from src.embeddings import EncoderManager
from src.retrieval import HybridRetriever, GraphRetriever
from src.generation import RAGGenerator
from src.ingestion import IngestionPipeline
from src.ontology.schema import NodeType
from .schemas import (
    QueryRequest, QueryResponse,
    IngestRequest, IngestResponse,
    EntityResponse, CompanyResponse
)

# Configure logging
logger.remove()
logger.add(sys.stderr, level=settings.log_level)
logger.add("logs/api.log", rotation="500 MB", level="INFO")

# Initialize FastAPI app
app = FastAPI(
    title="Multimodal Graph RAG for 10-K Reports",
    description="A production-ready Graph RAG system for SEC 10-K financial reports",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (initialized on startup)
neo4j_manager = None
qdrant_manager = None
hybrid_retriever = None
graph_retriever = None
rag_generator = None
ingestion_pipeline = None


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global neo4j_manager, qdrant_manager, hybrid_retriever
    global graph_retriever, rag_generator, ingestion_pipeline
    
    logger.info("Initializing components...")
    
    try:
        # Load configs
        model_config = load_yaml_config("config/model_config.yaml")
        
        # Initialize database managers
        neo4j_manager = Neo4jManager()
        neo4j_manager.create_indexes()
        
        qdrant_manager = QdrantManager()
        
        # Initialize encoder manager
        encoder_manager = EncoderManager(
            config=model_config["embeddings"]
        )
        
        # Try to create Qdrant collection
        try:
            qdrant_manager.create_collection(
                dense_dim=encoder_manager.get_dense_dim(),
                recreate=False
            )
        except Exception as e:
            logger.warning(f"Qdrant collection initialization: {e}")
        
        # Load retrieval config
        retrieval_config = {
            "rrf_k": 60,
            "dense_weight": 0.4,
            "sparse_weight": 0.3,
            "colbert_weight": 0.3
        }
        
        # Initialize retrievers
        hybrid_retriever = HybridRetriever(
            qdrant_manager,
            encoder_manager,
            config=retrieval_config
        )
        
        graph_retriever = GraphRetriever(neo4j_manager)
        
        # Initialize generator
        rag_generator = RAGGenerator()
        
        # Initialize ingestion pipeline
        ingestion_pipeline = IngestionPipeline(
            neo4j_manager,
            qdrant_manager
        )
        
        logger.info("All components initialized successfully!")
    
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down...")
    if neo4j_manager:
        neo4j_manager.close()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Multimodal Graph RAG API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check Neo4j
        neo4j_status = "connected" if neo4j_manager else "disconnected"
        
        # Check Qdrant
        qdrant_status = "connected" if qdrant_manager else "disconnected"
        
        return {
            "status": "healthy",
            "neo4j": neo4j_status,
            "qdrant": qdrant_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the system with a question about 10-K reports.
    
    Performs hybrid search and generates an answer with citations.
    """
    try:
        logger.info(f"Query received: {request.query}")
        
        # Hybrid search
        search_results = hybrid_retriever.search(
            query=request.query,
            top_k=request.top_k,
            filters=request.filters,
            strategy=request.strategy
        )
        
        # Get graph context if results have entity links
        graph_context = None
        if search_results:
            first_result = search_results[0]
            neo4j_ids = first_result.get("payload", {}).get("neo4j_node_ids", [])
            if neo4j_ids:
                graph_context = neo4j_manager.get_entity_context(neo4j_ids)
        
        # Generate answer
        result = rag_generator.generate(
            query=request.query,
            search_results=search_results,
            graph_context=graph_context
        )
        
        return QueryResponse(**result)
    
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestRequest):
    """
    Ingest a 10-K PDF document.
    
    Processes the document through extraction, ontology creation,
    embedding, and storage.
    """
    try:
        logger.info(f"Ingest request for: {request.file_path}")
        
        # Check if file exists
        if not Path(request.file_path).exists():
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        # Prepare metadata
        metadata = {
            "ticker": request.ticker,
            "filing_date": request.filing_date,
            "fiscal_year": request.fiscal_year
        }
        if request.metadata:
            metadata.update(request.metadata)
        
        # Run ingestion
        result = ingestion_pipeline.ingest_document(
            pdf_path=request.file_path,
            metadata=metadata
        )
        
        return IngestResponse(
            document_id=result["document_id"],
            file_name=result["file_name"],
            stats=result["stats"],
            message="Document ingested successfully"
        )
    
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/upload")
async def ingest_upload(
    file: UploadFile = File(...),
    ticker: str = None,
    filing_date: str = None,
    fiscal_year: int = None
):
    """
    Upload and ingest a 10-K PDF.
    
    Saves the uploaded file and processes it.
    """
    try:
        # Save uploaded file
        upload_dir = Path("data/raw")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"File uploaded: {file_path}")
        
        # Ingest
        metadata = {
            "ticker": ticker,
            "filing_date": filing_date,
            "fiscal_year": fiscal_year
        }
        
        result = ingestion_pipeline.ingest_document(
            pdf_path=str(file_path),
            metadata=metadata
        )
        
        return IngestResponse(
            document_id=result["document_id"],
            file_name=result["file_name"],
            stats=result["stats"],
            message="Document uploaded and ingested successfully"
        )
    
    except Exception as e:
        logger.error(f"Upload/ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/entities", response_model=EntityResponse)
async def get_entities(
    entity_type: str = None,
    limit: int = 100
):
    """
    Get extracted entities from the knowledge graph.
    
    Optionally filter by entity type.
    """
    try:
        if entity_type:
            query = f"""
            MATCH (n:{entity_type})
            RETURN n, labels(n) as labels
            LIMIT {limit}
            """
        else:
            query = f"""
            MATCH (n)
            WHERE n:Company OR n:Person OR n:Location OR n:FinancialMetric
            RETURN n, labels(n) as labels
            LIMIT {limit}
            """
        
        results = neo4j_manager.query_cypher(query)
        
        entities = []
        for record in results:
            entity = dict(record["n"])
            entity["type"] = record["labels"][0] if record["labels"] else "Unknown"
            entities.append(entity)
        
        return EntityResponse(
            entities=entities,
            total=len(entities)
        )
    
    except Exception as e:
        logger.error(f"Failed to get entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/companies/{ticker}", response_model=CompanyResponse)
async def get_company(ticker: str):
    """
    Get company overview from the knowledge graph.
    
    Includes metrics, executives, and subsidiaries.
    """
    try:
        # Get company entity
        company = neo4j_manager.get_entity_by_name(
            ticker,
            NodeType.COMPANY
        )
        
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Get related entities
        related = neo4j_manager.get_related_entities(
            ticker,
            max_depth=1
        )
        
        # Organize related entities
        metrics = []
        executives = []
        subsidiaries = []
        
        for entity in related:
            labels = entity.get("labels", [])
            if "FinancialMetric" in labels:
                metrics.append(entity)
            elif "Person" in labels:
                executives.append(entity)
            elif "Company" in labels:
                subsidiaries.append(entity.get("name", ""))
        
        return CompanyResponse(
            ticker=company.get("ticker", ticker),
            name=company.get("name", ""),
            sector=company.get("sector"),
            metrics=metrics[:10],
            executives=executives[:5],
            subsidiaries=subsidiaries[:10]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get company: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
