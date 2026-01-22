"""
Example usage of the REST API.
Demonstrates how to use the FastAPI endpoints.
"""
import requests
import json


API_URL = "http://localhost:8000"


def check_health():
    """Check API health."""
    response = requests.get(f"{API_URL}/health")
    print("Health Check:", response.json())


def ingest_document(pdf_path: str, ticker: str, filing_date: str, fiscal_year: int):
    """Ingest a 10-K document."""
    data = {
        "file_path": pdf_path,
        "ticker": ticker,
        "filing_date": filing_date,
        "fiscal_year": fiscal_year
    }
    
    response = requests.post(f"{API_URL}/ingest", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Ingestion successful!")
        print(f"Document ID: {result['document_id']}")
        print(f"Stats: {result['stats']}")
    else:
        print(f"Ingestion failed: {response.status_code}")
        print(response.text)


def query_system(query: str, top_k: int = 10):
    """Query the system."""
    data = {
        "query": query,
        "top_k": top_k,
        "strategy": "adaptive"
    }
    
    response = requests.post(f"{API_URL}/query", json=data)
    
    if response.status_code == 200:
        result = response.json()
        
        print("=" * 60)
        print(f"Query: {result['query']}")
        print("=" * 60)
        print("\nAnswer:")
        print(result['answer'])
        
        print("\n" + "=" * 60)
        print("Sources:")
        for source in result.get('sources', []):
            print(f"  - {source}")
        
        if result.get('usage'):
            print("\nUsage:")
            print(f"  Input tokens: {result['usage']['input_tokens']}")
            print(f"  Output tokens: {result['usage']['output_tokens']}")
    else:
        print(f"Query failed: {response.status_code}")
        print(response.text)


def get_entities(entity_type: str = None):
    """Get entities from knowledge graph."""
    params = {}
    if entity_type:
        params["entity_type"] = entity_type
    
    response = requests.get(f"{API_URL}/entities", params=params)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Total entities: {result['total']}")
        
        for entity in result['entities'][:10]:
            name = entity.get('name', 'N/A')
            ent_type = entity.get('type', 'Unknown')
            print(f"  - {name} ({ent_type})")
    else:
        print(f"Failed to get entities: {response.status_code}")


def get_company_info(ticker: str):
    """Get company information."""
    response = requests.get(f"{API_URL}/companies/{ticker}")
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\nCompany: {result['name']} ({result['ticker']})")
        print(f"Sector: {result.get('sector', 'N/A')}")
        
        print(f"\nMetrics ({len(result['metrics'])}):")
        for metric in result['metrics'][:5]:
            print(f"  - {metric.get('name', 'N/A')}: {metric.get('value', 'N/A')}")
        
        print(f"\nExecutives ({len(result['executives'])}):")
        for exec_person in result['executives'][:5]:
            print(f"  - {exec_person.get('name', 'N/A')} - {exec_person.get('role', 'N/A')}")
        
        print(f"\nSubsidiaries ({len(result['subsidiaries'])}):")
        for sub in result['subsidiaries'][:5]:
            print(f"  - {sub}")
    else:
        print(f"Failed to get company info: {response.status_code}")


def main():
    """Main example function."""
    print("=" * 60)
    print("Graph RAG API Usage Examples")
    print("=" * 60)
    
    # 1. Health check
    print("\n1. Health Check")
    check_health()
    
    # 2. Ingest a document (example - adjust path)
    print("\n2. Ingest Document")
    print("Example:")
    print("""
    ingest_document(
        pdf_path="data/raw/apple_10k_2024.pdf",
        ticker="AAPL",
        filing_date="2024-10-31",
        fiscal_year=2024
    )
    """)
    
    # 3. Query examples
    print("\n3. Query Examples")
    
    example_queries = [
        "What are Apple's main revenue sources?",
        "Compare revenue growth between Apple and Microsoft",
        "What risks does Apple face?",
        "Show me Apple's quarterly revenue breakdown"
    ]
    
    print("\nExample query:")
    query_system(example_queries[0])
    
    # 4. Get entities
    print("\n4. Get Entities")
    get_entities("Company")
    
    # 5. Get company info
    print("\n5. Get Company Info")
    print("Example:")
    print('get_company_info("AAPL")')


if __name__ == "__main__":
    main()
