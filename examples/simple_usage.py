"""
Simple usage example for the Graph RAG system.
Demonstrates basic ingestion and querying.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.databases import Neo4jManager, QdrantManager
from src.ingestion import IngestionPipeline
from src.embeddings import EncoderManager
from src.retrieval import HybridRetriever
from src.generation import RAGGenerator
from src.config import load_yaml_config


def main():
    """Main example function."""
    
    print("=" * 60)
    print("Multimodal Graph RAG - Simple Usage Example")
    print("=" * 60)
    
    # 1. Initialize components
    print("\n1. Initializing components...")
    
    neo4j = Neo4jManager()
    neo4j.create_indexes()
    
    qdrant = QdrantManager()
    
    model_config = load_yaml_config("config/model_config.yaml")
    encoder_manager = EncoderManager(config=model_config["embeddings"])
    
    # Create collection
    qdrant.create_collection(
        dense_dim=encoder_manager.get_dense_dim(),
        recreate=False
    )
    
    print("✓ Components initialized")
    
    # 2. Ingest a document (if you have a PDF)
    print("\n2. Document Ingestion")
    print("To ingest a 10-K PDF:")
    print("""
    pipeline = IngestionPipeline(neo4j, qdrant)
    
    result = pipeline.ingest_document(
        pdf_path="data/raw/apple_10k_2024.pdf",
        metadata={
            "ticker": "AAPL",
            "filing_date": "2024-10-31",
            "fiscal_year": 2024
        }
    )
    
    print(f"Ingested: {result['stats']}")
    """)
    
    # 3. Query the system
    print("\n3. Querying the System")
    
    # Initialize retrievers
    hybrid_retriever = HybridRetriever(
        qdrant,
        encoder_manager
    )
    
    rag_generator = RAGGenerator()
    
    # Example query
    query = "What are Apple's main revenue sources?"
    
    print(f"\nQuery: {query}")
    print("\nSearching...")
    
    # Hybrid search
    search_results = hybrid_retriever.search(
        query=query,
        top_k=5,
        strategy="adaptive"
    )
    
    print(f"Found {len(search_results)} results")
    
    # Get graph context if available
    graph_context = None
    if search_results and search_results[0].get("payload", {}).get("neo4j_node_ids"):
        neo4j_ids = search_results[0]["payload"]["neo4j_node_ids"]
        graph_context = neo4j.get_entity_context(neo4j_ids)
    
    # Generate answer
    print("\nGenerating answer...")
    result = rag_generator.generate(
        query=query,
        search_results=search_results,
        graph_context=graph_context
    )
    
    print("\n" + "=" * 60)
    print("ANSWER:")
    print("=" * 60)
    print(result["answer"])
    
    print("\n" + "=" * 60)
    print("SOURCES:")
    print("=" * 60)
    for source in result.get("sources", []):
        print(f"  - {source}")
    
    # 4. Graph queries
    print("\n" + "=" * 60)
    print("4. Graph Queries")
    print("=" * 60)
    
    # Example: Find all companies
    companies_query = """
    MATCH (c:Company)
    RETURN c.name, c.ticker, c.sector
    LIMIT 10
    """
    
    companies = neo4j.query_cypher(companies_query)
    
    if companies:
        print("\nCompanies in knowledge graph:")
        for company in companies:
            ticker = company.get("c.ticker", "N/A")
            name = company.get("c.name", "N/A")
            sector = company.get("c.sector", "N/A")
            print(f"  - {name} ({ticker}) - {sector}")
    else:
        print("\nNo companies found (ingest documents first)")
    
    # Cleanup
    print("\n" + "=" * 60)
    neo4j.close()
    print("Done!")


if __name__ == "__main__":
    main()
