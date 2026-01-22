# Quick Start Guide

Get your Multimodal Graph RAG system up and running in minutes!

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Step 2: Start Databases (Docker)

```bash
# Start both Neo4j and Qdrant
docker-compose up -d

# Or start individually:
# Neo4j
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 neo4j:latest

# Qdrant
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 \
  qdrant/qdrant:latest
```

Verify:
- Neo4j Browser: http://localhost:7474 (login: neo4j/password123)
- Qdrant Dashboard: http://localhost:6333/dashboard

### Step 3: Configure API Keys

```bash
cp .env.example .env
```

Edit `.env` and add:
```bash
# Required
OPENAI_API_KEY=sk-...
NEO4J_PASSWORD=password123

# Optional
QDRANT_HOST=localhost
QDRANT_PORT=6333
NEO4J_URI=bolt://localhost:7687
```

### Step 4: Test Installation

```bash
# Run a simple test
python examples/simple_usage.py
```

## 📋 Your First 10-K Ingestion

### Option A: Python API

```python
from src.databases import Neo4jManager, QdrantManager
from src.ingestion import IngestionPipeline
from src.config import load_yaml_config
from src.embeddings import EncoderManager

# Initialize
neo4j = Neo4jManager()
neo4j.create_indexes()

qdrant = QdrantManager()

# Load model config
model_config = load_yaml_config("config/model_config.yaml")
encoder_manager = EncoderManager(config=model_config["embeddings"])

# Create collection
qdrant.create_collection(
    dense_dim=encoder_manager.get_dense_dim()
)

# Ingest a 10-K
pipeline = IngestionPipeline(neo4j, qdrant)

result = pipeline.ingest_document(
    pdf_path="data/raw/apple_10k_2024.pdf",
    metadata={
        "ticker": "AAPL",
        "filing_date": "2024-10-31",
        "fiscal_year": 2024
    }
)

print(f"✓ Ingested {result['stats']['num_chunks']} chunks")
print(f"✓ Extracted {result['stats']['num_entities']} entities")
```

### Option B: REST API

**1. Start server:**
```bash
python src/api/server.py
```

**2. Upload and ingest:**
```bash
# Using curl
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "data/raw/apple_10k_2024.pdf",
    "ticker": "AAPL",
    "filing_date": "2024-10-31",
    "fiscal_year": 2024
  }'

# Or with Python
import requests

response = requests.post(
    "http://localhost:8000/ingest",
    json={
        "file_path": "data/raw/apple_10k_2024.pdf",
        "ticker": "AAPL",
        "filing_date": "2024-10-31",
        "fiscal_year": 2024
    }
)
print(response.json())
```

## 🔍 Your First Query

### Python API

```python
from src.retrieval import HybridRetriever
from src.generation import RAGGenerator

# Initialize (assuming neo4j, qdrant, encoder_manager from above)
retriever = HybridRetriever(qdrant, encoder_manager)
generator = RAGGenerator()

# Query
query = "What are Apple's main revenue sources?"

results = retriever.search(query, top_k=10)
answer = generator.generate(query, results)

print(answer["answer"])
print("\nSources:", answer["sources"])
```

### REST API

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are Apple'\''s main revenue sources?",
    "top_k": 10,
    "strategy": "adaptive"
  }'
```

## 🎯 Example Queries to Try

### 1. Keyword Search (SPARSE-heavy)
```
"Find all mentions of NVDA in 10-K filings"
"What is the exact EPS for Q4 2024?"
```

### 2. Semantic Search (DENSE-heavy)
```
"What are the main risks in the technology sector?"
"Explain Apple's competitive advantages"
```

### 3. Analytical (ColBERT-heavy)
```
"Compare revenue growth between Apple and Microsoft"
"Analyze the relationship between R&D spending and innovation"
```

### 4. Multimodal
```
"Show me revenue trend charts"
"Extract quarterly revenue breakdown from tables"
```

## 🗂️ Where to Put Your PDFs

```bash
# Create directory
mkdir -p data/raw

# Add your 10-K PDFs
cp ~/Downloads/apple_10k_2024.pdf data/raw/

# The system will create:
# data/extracted/    - Extracted tables, images
# data/processed/    - Processed chunks
```

## 🧪 Run Tests

```bash
# All tests
pytest

# Specific module
pytest tests/test_extraction.py

# With coverage
pytest --cov=src tests/

# Skip slow tests
pytest -m "not slow"
```

## 🔧 Troubleshooting

### Issue: "Can't connect to Neo4j"

**Solution:**
```bash
# Check if running
docker ps | grep neo4j

# Check logs
docker logs neo4j

# Restart
docker restart neo4j
```

### Issue: "Qdrant collection not found"

**Solution:**
```python
# Recreate collection
qdrant.create_collection(
    dense_dim=1024,  # or your embedding dimension
    recreate=True
)
```

### Issue: "Out of memory with ColBERT"

**Solution:**
Edit `config/model_config.yaml`:
```yaml
embeddings:
  colbert:
    batch_size: 8  # Reduce from 16
```

### Issue: "Vision API failing"

**Solution:**
Disable vision temporarily:
```python
extractor = PDFExtractor(
    config=extraction_config,
    use_vision=False  # Disable Claude Vision
)
```

## 📊 Monitor Progress

### Check ingestion progress:
```python
# View logs
tail -f logs/api.log

# Check database sizes
# Neo4j Browser: http://localhost:7474
MATCH (n) RETURN count(n)  # Total nodes

# Qdrant Dashboard: http://localhost:6333/dashboard
```

## 🎓 Next Steps

1. **Read the full README**: `README.md`
2. **Explore examples**: `examples/simple_usage.py`, `examples/api_usage.py`
3. **Customize configs**: `config/` directory
4. **Review API docs**: http://localhost:8000/docs (when server is running)

## 💡 Tips

1. **Start small**: Ingest 1-2 documents first to test
2. **Use adaptive strategy**: Let the system choose the best search method
3. **Monitor resources**: Neo4j and Qdrant can be memory-intensive
4. **Cache embeddings**: Enable in config for faster repeated queries
5. **Batch processing**: Use `pipeline.batch_ingest()` for multiple files

## 🆘 Need Help?

- Check `README.md` for detailed documentation
- Review API docs at `/docs` endpoint
- Open an issue on GitHub
- Check logs in `logs/` directory

Happy analyzing! 🚀
