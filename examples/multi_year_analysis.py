"""
Multi-year historical analysis example.
Demonstrates ingesting and analyzing multiple 10-K filings across years.
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


def ingest_multi_year_example():
    """Example: Ingest multiple years of 10-K filings."""
    
    print("=" * 70)
    print("Multi-Year 10-K Ingestion Example")
    print("=" * 70)
    
    # Initialize components
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
    
    pipeline = IngestionPipeline(neo4j, qdrant)
    
    print("✓ Components initialized")
    
    # Define multi-year documents to ingest
    documents = [
        {
            "pdf_path": "data/raw/aapl_10k_2022.pdf",
            "metadata": {
                "ticker": "AAPL",
                "company_name": "Apple Inc.",
                "fiscal_year": 2022,
                "filing_date": "2022-10-28",
                "sector": "Technology"
            }
        },
        {
            "pdf_path": "data/raw/aapl_10k_2023.pdf",
            "metadata": {
                "ticker": "AAPL",
                "company_name": "Apple Inc.",
                "fiscal_year": 2023,
                "filing_date": "2023-11-03",
                "sector": "Technology"
            }
        },
        {
            "pdf_path": "data/raw/aapl_10k_2024.pdf",
            "metadata": {
                "ticker": "AAPL",
                "company_name": "Apple Inc.",
                "fiscal_year": 2024,
                "filing_date": "2024-10-31",
                "sector": "Technology"
            }
        }
    ]
    
    # Ingest each year
    print("\n2. Ingesting documents...")
    ingestion_results = []
    
    for doc in documents:
        # Check if file exists
        if not Path(doc["pdf_path"]).exists():
            print(f"⚠️  Skipping {doc['metadata']['fiscal_year']}: File not found")
            print(f"   Place your PDF at: {doc['pdf_path']}")
            continue
        
        print(f"\nIngesting {doc['metadata']['ticker']} {doc['metadata']['fiscal_year']}...")
        
        try:
            result = pipeline.ingest_document(
                pdf_path=doc["pdf_path"],
                metadata=doc["metadata"]
            )
            
            ingestion_results.append(result)
            
            print(f"✓ Completed:")
            print(f"  - Chunks: {result['stats']['num_chunks']}")
            print(f"  - Entities: {result['stats']['num_entities']}")
            print(f"  - Relationships: {result['stats']['num_relationships']}")
        
        except Exception as e:
            print(f"✗ Failed: {e}")
    
    if not ingestion_results:
        print("\n⚠️  No documents were ingested. Add PDFs to data/raw/ directory.")
        print("\nExample structure:")
        print("  data/raw/aapl_10k_2022.pdf")
        print("  data/raw/aapl_10k_2023.pdf")
        print("  data/raw/aapl_10k_2024.pdf")
        return None, None
    
    print(f"\n✓ Successfully ingested {len(ingestion_results)} documents")
    
    # Clean up
    neo4j.close()
    
    return ingestion_results


def query_historical_example():
    """Example: Query across multiple years."""
    
    print("\n" + "=" * 70)
    print("Historical Analysis Queries")
    print("=" * 70)
    
    # Initialize
    neo4j = Neo4jManager()
    qdrant = QdrantManager()
    
    model_config = load_yaml_config("config/model_config.yaml")
    encoder_manager = EncoderManager(config=model_config["embeddings"])
    
    retriever = HybridRetriever(qdrant, encoder_manager)
    generator = RAGGenerator()
    
    # Example queries
    queries = [
        {
            "query": "What was Apple's revenue in fiscal year 2024?",
            "filters": {"company_ticker": "AAPL", "fiscal_year": 2024},
            "description": "Single Year Analysis"
        },
        {
            "query": "How has Apple's revenue grown over the past 3 years?",
            "filters": {"company_ticker": "AAPL"},
            "description": "Multi-Year Trend Analysis"
        },
        {
            "query": "What are the key differences in Apple's risk factors between 2022 and 2024?",
            "filters": {"company_ticker": "AAPL", "section": "Item_1A"},
            "description": "Comparative Analysis"
        }
    ]
    
    for i, q in enumerate(queries, 1):
        print(f"\n{i}. {q['description']}")
        print(f"   Query: {q['query']}")
        print(f"   Filters: {q['filters']}")
        print("\n   Searching...")
        
        try:
            # Search
            results = retriever.search(
                query=q["query"],
                filters=q.get("filters"),
                top_k=10
            )
            
            print(f"   Found {len(results)} relevant chunks")
            
            # Get graph context
            graph_context = None
            if results and results[0].get("payload", {}).get("neo4j_node_ids"):
                neo4j_ids = results[0]["payload"]["neo4j_node_ids"]
                graph_context = neo4j.get_entity_context(neo4j_ids)
                print(f"   Graph context: {len(graph_context.get('entities', []))} entities")
            
            # Generate answer
            print("   Generating answer...\n")
            answer = generator.generate(
                query=q["query"],
                search_results=results,
                graph_context=graph_context
            )
            
            print("   " + "-" * 66)
            print("   ANSWER:")
            print("   " + "-" * 66)
            
            # Print answer with indentation
            for line in answer["answer"].split("\n"):
                print(f"   {line}")
            
            print("\n   " + "-" * 66)
            print("   SOURCES:")
            print("   " + "-" * 66)
            for source in answer.get("sources", [])[:3]:
                print(f"   - {source}")
            
            if len(answer.get("sources", [])) > 3:
                print(f"   ... and {len(answer['sources']) - 3} more")
        
        except Exception as e:
            print(f"   ✗ Query failed: {e}")
    
    # Clean up
    neo4j.close()


def graph_temporal_queries():
    """Example: Direct graph queries for temporal data."""
    
    print("\n" + "=" * 70)
    print("Graph Database: Temporal Queries")
    print("=" * 70)
    
    neo4j = Neo4jManager()
    
    # Query 1: All financial metrics across years
    print("\n1. Financial Metrics Timeline")
    query1 = """
    MATCH (c:Company {ticker: 'AAPL'})-[:REPORTS_METRIC]->(m:FinancialMetric)
    WHERE m.fiscal_year IS NOT NULL
    RETURN m.name as metric, 
           m.value as value, 
           m.unit as unit,
           m.fiscal_year as year
    ORDER BY m.fiscal_year DESC, m.name
    LIMIT 20
    """
    
    try:
        results = neo4j.query_cypher(query1)
        
        if results:
            print("\n   Metric                          Year    Value")
            print("   " + "-" * 60)
            for r in results:
                metric = r.get("metric", "Unknown")[:30]
                year = r.get("year", "N/A")
                value = r.get("value", "N/A")
                unit = r.get("unit", "")
                print(f"   {metric:<30} {year}    {value} {unit}")
        else:
            print("   No metrics found. Ingest documents first.")
    
    except Exception as e:
        print(f"   Error: {e}")
    
    # Query 2: Entity counts by year
    print("\n2. Data Coverage by Year")
    query2 = """
    MATCH (c:Company {ticker: 'AAPL'})-[:REPORTS_METRIC]->(m:FinancialMetric)
    WHERE m.fiscal_year IS NOT NULL
    WITH m.fiscal_year as year, count(*) as metric_count
    OPTIONAL MATCH (c:Company {ticker: 'AAPL'})-[:HAS_EXECUTIVE]->(p:Person)
    WITH year, metric_count, count(DISTINCT p) as exec_count
    RETURN year, metric_count, exec_count
    ORDER BY year DESC
    """
    
    try:
        results = neo4j.query_cypher(query2)
        
        if results:
            print("\n   Year    Metrics    Executives")
            print("   " + "-" * 35)
            for r in results:
                year = r.get("year", "N/A")
                metrics = r.get("metric_count", 0)
                execs = r.get("exec_count", 0)
                print(f"   {year}    {metrics:<10} {execs}")
        else:
            print("   No data found.")
    
    except Exception as e:
        print(f"   Error: {e}")
    
    neo4j.close()


def main():
    """Main example workflow."""
    
    print("\n" + "=" * 70)
    print("Multi-Year 10-K Analysis - Complete Example")
    print("=" * 70)
    
    # Step 1: Ingest
    print("\nStep 1: Ingest multiple years of 10-K documents")
    print("-" * 70)
    
    ingestion_results = ingest_multi_year_example()
    
    if ingestion_results:
        # Step 2: Query
        print("\nStep 2: Historical analysis queries")
        print("-" * 70)
        
        query_historical_example()
        
        # Step 3: Graph queries
        print("\nStep 3: Direct graph temporal queries")
        print("-" * 70)
        
        graph_temporal_queries()
    
    print("\n" + "=" * 70)
    print("Example Complete!")
    print("=" * 70)
    
    print("\nKey Takeaways:")
    print("1. ✓ System handles multiple years seamlessly")
    print("2. ✓ Temporal metadata (fiscal_year) enables filtering")
    print("3. ✓ Graph queries reveal year-over-year patterns")
    print("4. ✓ RAG synthesizes insights across years")
    print("\nFor more details, see: HISTORICAL_ANALYSIS_GUIDE.md")


if __name__ == "__main__":
    main()
