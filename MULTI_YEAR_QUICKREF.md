# Multi-Year Analysis - Quick Reference

## ✅ YES - Fully Supported!

The system **fully supports** multi-year 10-K ingestion and historical analysis out-of-the-box.

---

## 🚀 Quick Start (3 Steps)

### 1. Ingest Multiple Years

```python
from src.databases import Neo4jManager, QdrantManager
from src.ingestion import IngestionPipeline

neo4j = Neo4jManager()
qdrant = QdrantManager()
pipeline = IngestionPipeline(neo4j, qdrant)

# Ingest multiple years
for year in [2020, 2021, 2022, 2023, 2024]:
    pipeline.ingest_document(
        pdf_path=f"data/raw/aapl_10k_{year}.pdf",
        metadata={
            "ticker": "AAPL",
            "fiscal_year": year,
            "filing_date": f"{year}-10-31"
        }
    )
```

### 2. Query Specific Year

```python
from src.retrieval import HybridRetriever

results = retriever.search(
    query="What was Apple's revenue?",
    filters={"fiscal_year": 2024, "company_ticker": "AAPL"}
)
```

### 3. Query Across Years (Historical Analysis)

```python
# No year filter = get all years
results = retriever.search(
    query="How has Apple's revenue grown over time?",
    filters={"company_ticker": "AAPL"},  # No fiscal_year filter!
    top_k=20  # Get more results to cover multiple years
)
```

---

## 📊 What Gets Stored Per Year

Each document ingestion stores:

**In Qdrant (per chunk):**
- `fiscal_year`: 2024
- `filing_date`: "2024-10-31"
- `company_ticker`: "AAPL"
- Text, tables, charts with full context

**In Neo4j (entities):**
- Company nodes (one per company)
- FinancialMetric nodes with `fiscal_year` property
- Relationships with `temporal_validity`

**Result:** Data from all years coexists and can be queried individually or together.

---

## 🔍 Common Query Patterns

### Single Year Analysis
```python
filters={"fiscal_year": 2024, "company_ticker": "AAPL"}
```

### Multi-Year Comparison
```python
# Method 1: Let RAG synthesize
filters={"company_ticker": "AAPL"}  # No year filter

# Method 2: Graph query
query = """
MATCH (c:Company {ticker: 'AAPL'})-[:REPORTS_METRIC]->(m:FinancialMetric)
WHERE m.fiscal_year IN [2022, 2023, 2024]
RETURN m.name, m.value, m.fiscal_year
ORDER BY m.fiscal_year
"""
```

### Trend Analysis
```python
query = "What is the 5-year trend in Apple's R&D spending?"
filters = {"company_ticker": "AAPL", "section": "Item_7_MD&A"}
# System will pull data from all available years
```

### Year Range
```python
# Using Qdrant (would need custom filter implementation)
# OR use graph query:
"""
WHERE m.fiscal_year >= 2020 AND m.fiscal_year <= 2024
"""
```

---

## 🎯 How It Works

### Data Isolation by Year
- Each PDF creates separate chunks with its year
- Same entity (e.g., "Apple Inc.") links to all years
- Metrics have `fiscal_year` property for filtering

### Cross-Year Entity Linking
```
Company: Apple Inc. (one node)
    ├─ REPORTS_METRIC → Revenue (fiscal_year: 2022)
    ├─ REPORTS_METRIC → Revenue (fiscal_year: 2023)
    └─ REPORTS_METRIC → Revenue (fiscal_year: 2024)
```

### Historical Queries
- **Qdrant**: Filters by `fiscal_year` in payload
- **Neo4j**: Uses `WHERE m.fiscal_year = X` in Cypher
- **RAG**: Synthesizes across years when no filter is set

---

## 💡 Pro Tips

### 1. Batch Ingestion
```python
years = range(2020, 2025)
docs = [{"pdf_path": f"data/raw/aapl_{y}.pdf", 
         "metadata": {"ticker": "AAPL", "fiscal_year": y}} 
        for y in years]

for doc in docs:
    pipeline.ingest_document(**doc)
```

### 2. Get Historical Metrics from Graph
```python
# Fast structured data retrieval
query = """
MATCH (c:Company {ticker: $ticker})-[:REPORTS_METRIC]->(m)
WHERE m.fiscal_year >= $start AND m.fiscal_year <= $end
RETURN m.fiscal_year, m.name, m.value
ORDER BY m.fiscal_year, m.name
"""
```

### 3. Multi-Company Temporal Comparison
```python
# Ingest multiple companies
for ticker in ["AAPL", "MSFT", "GOOGL"]:
    for year in [2022, 2023, 2024]:
        pipeline.ingest_document(...)

# Query across companies
results = retriever.search(
    "Compare revenue growth of AAPL, MSFT, and GOOGL",
    top_k=30  # Get enough for all companies/years
)
```

---

## 📈 Example Outputs

### Query: "What was Apple's revenue in 2024?"
**Filter:** `{"fiscal_year": 2024}`
**Result:** Only 2024 data

### Query: "How has Apple's revenue changed?"
**Filter:** `{"company_ticker": "AAPL"}` (no year)
**Result:** Data from all years, synthesized into trend analysis

### Query: "Compare 2023 and 2024 risk factors"
**Filter:** None or `{"fiscal_year": [2023, 2024]}`
**Result:** Risk sections from both years for comparison

---

## 🔧 Optional Enhancements

While the system works great as-is, you can add:

1. **YoY Relationships** - Create explicit year-over-year links in graph
2. **Temporal Reranking** - Boost recent documents for current queries
3. **Time Series Retriever** - Specialized component for trend queries
4. **Visualization Prep** - Structure data for charts

See `HISTORICAL_ANALYSIS_GUIDE.md` for implementation details.

---

## 📖 See Also

- **Full Guide:** `HISTORICAL_ANALYSIS_GUIDE.md`
- **Example Code:** `examples/multi_year_analysis.py`
- **API Usage:** Use `/query` endpoint with `filters` parameter

---

## ✅ Bottom Line

**The system is ready for multi-year analysis RIGHT NOW.**

Just ingest your documents with `fiscal_year` in metadata, and you can:
- ✓ Filter by specific years
- ✓ Compare across years  
- ✓ Analyze trends
- ✓ Track changes over time
- ✓ Get historical context in answers

No additional setup required! 🚀
