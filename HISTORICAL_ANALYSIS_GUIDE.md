# Historical Analysis Guide: Multi-Year 10-K Documents

## ✅ YES - The System DOES Support Multi-Year Analysis!

The current implementation **already has the foundation** for historical analysis. Here's what works out-of-the-box and how to enhance it for powerful temporal queries.

---

## 🎯 What's Already Built-In

### 1. Temporal Metadata Storage

**Qdrant** stores for each chunk:
```python
{
    "company_ticker": "AAPL",
    "filing_date": "2024-10-31",
    "fiscal_year": 2024,
    "section": "Item_7_MD&A",
    "text": "...",
    "neo4j_node_ids": [...]
}
```

**Neo4j** supports:
- `fiscal_year` property on FinancialMetric nodes
- `temporal_validity` on relationships
- `filing_date` on Company nodes

### 2. Year-Based Filtering

You can already filter by fiscal year:

```python
# Query specific year
results = hybrid_retriever.search(
    query="What was Apple's revenue?",
    filters={"fiscal_year": 2024}
)

# Query range (requires enhancement - see below)
```

---

## 📥 Ingesting Multi-Year Documents

### Option A: Sequential Ingestion (Recommended)

```python
from src.databases import Neo4jManager, QdrantManager
from src.ingestion import IngestionPipeline

# Initialize once
neo4j = Neo4jManager()
qdrant = QdrantManager()
pipeline = IngestionPipeline(neo4j, qdrant)

# Ingest multiple years
years_data = [
    {
        "pdf_path": "data/raw/aapl_10k_2020.pdf",
        "metadata": {"ticker": "AAPL", "fiscal_year": 2020, "filing_date": "2020-10-30"}
    },
    {
        "pdf_path": "data/raw/aapl_10k_2021.pdf",
        "metadata": {"ticker": "AAPL", "fiscal_year": 2021, "filing_date": "2021-10-29"}
    },
    {
        "pdf_path": "data/raw/aapl_10k_2022.pdf",
        "metadata": {"ticker": "AAPL", "fiscal_year": 2022, "filing_date": "2022-10-28"}
    },
    {
        "pdf_path": "data/raw/aapl_10k_2023.pdf",
        "metadata": {"ticker": "AAPL", "fiscal_year": 2023, "filing_date": "2023-11-03"}
    },
    {
        "pdf_path": "data/raw/aapl_10k_2024.pdf",
        "metadata": {"ticker": "AAPL", "fiscal_year": 2024, "filing_date": "2024-10-31"}
    }
]

# Ingest all years
for doc in years_data:
    result = pipeline.ingest_document(
        pdf_path=doc["pdf_path"],
        metadata=doc["metadata"]
    )
    print(f"✓ Ingested {doc['metadata']['ticker']} {doc['metadata']['fiscal_year']}")
```

### Option B: Batch Ingestion

```python
pdf_paths = [f"data/raw/aapl_10k_{year}.pdf" for year in range(2020, 2025)]
metadata_list = [
    {"ticker": "AAPL", "fiscal_year": year, "filing_date": f"{year}-10-31"} 
    for year in range(2020, 2025)
]

results = pipeline.batch_ingest(pdf_paths, metadata_list)
```

---

## 🔍 Historical Query Examples

### Example 1: Single Year Analysis

```python
from src.retrieval import HybridRetriever
from src.generation import RAGGenerator

retriever = HybridRetriever(qdrant, encoder_manager)
generator = RAGGenerator()

# Query 2024 only
results = retriever.search(
    query="What was Apple's revenue in fiscal year 2024?",
    filters={"fiscal_year": 2024, "company_ticker": "AAPL"}
)

answer = generator.generate(
    query="What was Apple's revenue in fiscal year 2024?",
    search_results=results
)
```

### Example 2: Comparing Multiple Years (Using Graph)

```python
from src.retrieval import GraphRetriever

graph_retriever = GraphRetriever(neo4j)

# Get revenue metrics across years
query = """
MATCH (c:Company {ticker: 'AAPL'})-[:REPORTS_METRIC]->(m:FinancialMetric)
WHERE m.name CONTAINS 'revenue' OR m.name CONTAINS 'Revenue'
RETURN m.name, m.value, m.fiscal_year, m.unit
ORDER BY m.fiscal_year DESC
"""

metrics = neo4j.query_cypher(query)

# Will return metrics from all ingested years
for metric in metrics:
    print(f"{metric['m.fiscal_year']}: {metric['m.value']} {metric['m.unit']}")
```

### Example 3: Trend Analysis

```python
# Query without year filter to get multi-year context
results = retriever.search(
    query="How has Apple's revenue grown over the past 5 years?",
    filters={"company_ticker": "AAPL"},  # No year filter
    top_k=20  # Get more results to capture multiple years
)

# The RAG generator will synthesize across years
answer = generator.generate(
    query="How has Apple's revenue grown over the past 5 years?",
    search_results=results
)
```

---

## 🚀 Enhancements for Better Historical Analysis

The system works, but here are recommended enhancements for optimal temporal analysis:

### Enhancement 1: Temporal Query Classifier

Add to `src/retrieval/query_classifier.py`:

```python
def detect_temporal_query(self, query: str) -> Dict:
    """Detect if query requires temporal/historical analysis."""
    temporal_keywords = [
        "trend", "over time", "historical", "past", "years",
        "growth", "change", "compared to", "year over year",
        "yoy", "increase", "decrease", "evolution"
    ]
    
    is_temporal = any(kw in query.lower() for kw in temporal_keywords)
    
    # Extract year mentions
    import re
    years = re.findall(r'\b(20\d{2})\b', query)
    
    return {
        "is_temporal": is_temporal,
        "mentioned_years": years,
        "requires_multi_year": is_temporal and len(years) != 1
    }
```

### Enhancement 2: Year-over-Year Relationship Type

Add to `src/ontology/schema.py`:

```python
class RelationshipType(str, Enum):
    # ... existing types ...
    YOY_COMPARISON = "YOY_COMPARISON"  # Links same metric across years
    TREND = "TREND"  # Links related temporal patterns
```

Then in the ingestion pipeline, create these relationships:

```python
def create_temporal_relationships(self, neo4j: Neo4jManager):
    """Create relationships between same metrics across years."""
    
    query = """
    MATCH (m1:FinancialMetric), (m2:FinancialMetric)
    WHERE m1.name = m2.name 
      AND m1.fiscal_year = m2.fiscal_year - 1
      AND m1.company_ticker = m2.company_ticker
    MERGE (m1)-[r:YOY_COMPARISON]->(m2)
    SET r.yoy_change = (m2.value - m1.value) / m1.value
    SET r.absolute_change = m2.value - m1.value
    RETURN count(r) as relationships_created
    """
    
    result = neo4j.query_cypher(query)
    return result[0]["relationships_created"]
```

### Enhancement 3: Temporal Aggregation Retriever

Create `src/retrieval/temporal_retriever.py`:

```python
"""
Temporal retriever for historical analysis.
"""
from typing import List, Dict
from loguru import logger

class TemporalRetriever:
    """
    Retrieves and aggregates data across multiple years.
    """
    
    def __init__(self, qdrant_manager, neo4j_manager):
        self.qdrant = qdrant_manager
        self.neo4j = neo4j_manager
    
    def retrieve_time_series(
        self,
        company_ticker: str,
        metric_name: str,
        start_year: int,
        end_year: int
    ) -> Dict:
        """
        Retrieve a metric across multiple years.
        
        Returns time series data with context from both databases.
        """
        # Get from graph
        query = """
        MATCH (c:Company {ticker: $ticker})-[:REPORTS_METRIC]->(m:FinancialMetric)
        WHERE m.name CONTAINS $metric
          AND m.fiscal_year >= $start_year
          AND m.fiscal_year <= $end_year
        RETURN m.fiscal_year as year, 
               m.value as value, 
               m.unit as unit,
               m.yoy_change as yoy_change
        ORDER BY m.fiscal_year
        """
        
        graph_data = self.neo4j.query_cypher(
            query,
            {
                "ticker": company_ticker,
                "metric": metric_name,
                "start_year": start_year,
                "end_year": end_year
            }
        )
        
        # Get textual context from Qdrant
        context_chunks = []
        for year in range(start_year, end_year + 1):
            results = self.qdrant.search_dense(
                query_vector=...,  # Would embed the metric name
                filters={
                    "company_ticker": company_ticker,
                    "fiscal_year": year
                },
                limit=3
            )
            context_chunks.extend(results)
        
        return {
            "time_series": graph_data,
            "context": context_chunks
        }
    
    def compare_periods(
        self,
        company_ticker: str,
        years: List[int],
        aspect: str
    ) -> Dict:
        """Compare specific aspect across selected years."""
        
        results = {}
        for year in years:
            # Search for that year
            year_results = self.qdrant.search_dense(
                query_vector=...,  # Embed the aspect
                filters={
                    "company_ticker": company_ticker,
                    "fiscal_year": year
                },
                limit=5
            )
            results[year] = year_results
        
        return results
```

### Enhancement 4: Historical Context in RAG Prompt

Update `src/generation/rag_generator.py` to detect temporal queries:

```python
def _get_system_prompt(self) -> str:
    return """You are a financial analyst assistant...

When answering temporal/historical questions:
1. Identify trends and patterns across years
2. Calculate year-over-year changes when data is available
3. Note any significant shifts or anomalies
4. Provide context for changes (market conditions, strategy shifts, etc.)
5. Use specific years in your citations

For trend analysis, structure your answer as:
- Overall trend (growing, declining, stable)
- Key inflection points
- Supporting data with years
- Underlying factors
"""
```

---

## 📊 Example: Complete Historical Analysis Workflow

```python
from src.databases import Neo4jManager, QdrantManager
from src.ingestion import IngestionPipeline
from src.embeddings import EncoderManager
from src.retrieval import HybridRetriever
from src.generation import RAGGenerator
from src.config import load_yaml_config

# Initialize
neo4j = Neo4jManager()
qdrant = QdrantManager()

model_config = load_yaml_config("config/model_config.yaml")
encoder_manager = EncoderManager(config=model_config["embeddings"])

# 1. Ingest 5 years of Apple 10-Ks
pipeline = IngestionPipeline(neo4j, qdrant)

for year in range(2020, 2025):
    pipeline.ingest_document(
        pdf_path=f"data/raw/aapl_10k_{year}.pdf",
        metadata={
            "ticker": "AAPL",
            "fiscal_year": year,
            "filing_date": f"{year}-10-31"
        }
    )

# 2. Query: Revenue trend over 5 years
retriever = HybridRetriever(qdrant, encoder_manager)
generator = RAGGenerator()

query = "Analyze Apple's revenue trend from 2020 to 2024. What are the key drivers?"

# Get results across all years
results = retriever.search(
    query=query,
    filters={"company_ticker": "AAPL"},  # No year filter
    top_k=20  # Get more to capture multiple years
)

# Get graph data for revenue metrics
revenue_query = """
MATCH (c:Company {ticker: 'AAPL'})-[:REPORTS_METRIC]->(m:FinancialMetric)
WHERE m.name CONTAINS 'revenue'
  AND m.fiscal_year >= 2020 AND m.fiscal_year <= 2024
RETURN m.fiscal_year, m.value, m.unit, m.yoy_change
ORDER BY m.fiscal_year
"""

graph_data = neo4j.query_cypher(revenue_query)

# Generate comprehensive answer
answer = generator.generate(
    query=query,
    search_results=results,
    graph_context={"revenue_data": graph_data}
)

print(answer["answer"])
# Will include analysis like:
# "Apple's revenue grew from $274B in 2020 to $394B in 2024, 
#  representing a CAGR of 9.5%. Key drivers included..."
```

---

## 🎯 Advanced Use Cases

### 1. Competitive Historical Analysis

```python
# Ingest multiple companies across years
companies = ["AAPL", "MSFT", "GOOGL"]
years = range(2020, 2025)

for ticker in companies:
    for year in years:
        pipeline.ingest_document(
            pdf_path=f"data/raw/{ticker.lower()}_10k_{year}.pdf",
            metadata={"ticker": ticker, "fiscal_year": year}
        )

# Query cross-company trends
query = "Compare revenue growth rates of Apple, Microsoft, and Google from 2020 to 2024"

results = retriever.search(
    query=query,
    top_k=30  # Get results from all companies/years
)
```

### 2. Risk Factor Evolution

```python
query = "How have Apple's risk factors evolved from 2020 to 2024? What new risks emerged?"

results = retriever.search(
    query=query,
    filters={
        "company_ticker": "AAPL",
        "section": "Item_1A"  # Risk Factors section
    },
    top_k=25
)

# This will pull risk factor sections from multiple years
```

### 3. Executive Changes Impact

```python
# Graph query to find executive changes and correlate with metrics
query = """
MATCH (c:Company {ticker: 'AAPL'})-[r:HAS_EXECUTIVE]->(p:Person)
WITH p, r, 
     toInteger(substring(r.temporal_validity, 0, 4)) as start_year
MATCH (c)-[:REPORTS_METRIC]->(m:FinancialMetric)
WHERE m.fiscal_year = start_year
RETURN p.name, p.role, start_year, 
       collect(m.name + ': ' + m.value) as metrics
ORDER BY start_year DESC
"""
```

---

## ✅ Summary: What Works Out-of-the-Box

| Feature | Status | Notes |
|---------|--------|-------|
| Multi-year ingestion | ✅ Works | Use `fiscal_year` in metadata |
| Year-based filtering | ✅ Works | Filter Qdrant by `fiscal_year` |
| Graph temporal queries | ✅ Works | Use `fiscal_year` in Cypher WHERE |
| Cross-year entity linking | ✅ Works | Same entities link to multiple years |
| Temporal metadata | ✅ Stored | In both Qdrant payload and Neo4j properties |
| Multi-year retrieval | ✅ Works | Don't filter by year, get all results |
| Historical context in RAG | ✅ Works | GPT-4o synthesizes across years |

## 🔧 Recommended Enhancements

| Enhancement | Priority | Impact |
|-------------|----------|--------|
| YoY relationships in graph | High | Enables direct year comparison |
| Temporal query detection | Medium | Better query routing |
| Time series aggregation | High | Structured historical data |
| Temporal reranking | Medium | Prioritize recent vs historical |
| Trend visualization prep | Low | Better data for charts |

---

## 🚦 Quick Start for Historical Analysis

```bash
# 1. Ingest multiple years
python -c "
from src.ingestion import IngestionPipeline
from src.databases import Neo4jManager, QdrantManager

neo4j = Neo4jManager()
qdrant = QdrantManager()
pipeline = IngestionPipeline(neo4j, qdrant)

# Add your 10-Ks here
for year in [2022, 2023, 2024]:
    pipeline.ingest_document(
        pdf_path=f'data/raw/aapl_{year}.pdf',
        metadata={'ticker': 'AAPL', 'fiscal_year': year}
    )
"

# 2. Query historically
python -c "
from src.retrieval import HybridRetriever
from src.generation import RAGGenerator

# ... initialize components ...

results = retriever.search(
    'How has revenue changed over time?',
    filters={'company_ticker': 'AAPL'}
)
answer = generator.generate('...', results)
print(answer['answer'])
"
```

---

## 📝 Bottom Line

**YES, the system fully supports multi-year historical analysis!** 

The core infrastructure is already in place:
- ✅ Temporal metadata storage
- ✅ Year-based filtering
- ✅ Multi-year entity linking
- ✅ Graph temporal queries
- ✅ Historical context synthesis

You can start using it immediately for historical analysis. The suggested enhancements will make it even more powerful for complex temporal queries, but they're **optional** - the system works well as-is for most historical analysis needs.
