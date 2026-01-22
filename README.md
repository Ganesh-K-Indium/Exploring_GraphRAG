# Multimodal Graph RAG for 10-K Reports

A production-ready Graph RAG system that processes SEC 10-K reports with **multimodal extraction** (text, tables, images/charts) from PDFs. Combines graph-based ontology with multi-vector embeddings (dense, sparse, ColBERT) for comprehensive financial document analysis.

## 🌟 Features

### Core Capabilities

- **Multimodal PDF Extraction**: Extracts text, tables, images, and financial charts from 10-K PDFs
- **Intelligent Ontology Creation**: Uses NER + LLM to extract entities and relationships
- **Multi-Vector Embeddings**: 
  - Dense embeddings (OpenAI text-embedding-3-large) for semantic search
  - Sparse embeddings (SPLADE) for keyword/exact matching
  - ColBERT late interaction for fine-grained retrieval
- **Hybrid Graph + Vector Search**: Combines Neo4j knowledge graph with Qdrant vector database
- **Adaptive Query Classification**: Automatically determines optimal search strategy
- **Claude-Powered RAG**: Generates answers with proper citations from multimodal context

### Production-Ready

- ✅ FastAPI REST API
- ✅ Comprehensive error handling
- ✅ Structured logging
- ✅ Type hints throughout
- ✅ Modular architecture
- ✅ Configuration management
- ✅ Batch processing support

## 🏗️ Architecture

```
PDF → Multimodal Extraction → Ontology → Multi-Vector Embeddings → Neo4j + Qdrant → Hybrid Retrieval → RAG Generation
```

### Components

1. **Extraction Layer** (`src/extraction/`)
   - PDF text extraction (pypdf/pdfplumber)
   - Table extraction (pdfplumber)
   - Image/chart extraction (PyMuPDF)
   - Claude Vision for chart analysis

2. **Ontology Layer** (`src/ontology/`)
   - NER extraction (spaCy)
   - LLM relationship extraction (Claude)
   - Entity resolution and deduplication

3. **Embedding Layer** (`src/embeddings/`)
   - Dense embedder (Voyage AI / OpenAI)
   - Sparse embedder (SPLADE)
   - ColBERT embedder
   - Encoder manager (orchestrates all three)

4. **Database Layer** (`src/databases/`)
   - Neo4j manager (graph storage)
   - Qdrant manager (vector storage)
   - Database linker (bidirectional linking)

5. **Retrieval Layer** (`src/retrieval/`)
   - Query classifier (adaptive strategy)
   - Hybrid retriever (multi-vector fusion)
   - Graph retriever (Cypher queries)
   - Reranker (multi-factor scoring)

6. **Generation Layer** (`src/generation/`)
   - Context builder (multimodal formatting)
   - RAG generator (Claude-based)

7. **Ingestion Pipeline** (`src/ingestion/`)
   - End-to-end orchestration

8. **API Layer** (`src/api/`)
   - FastAPI server
   - REST endpoints

## 📦 Installation

### Prerequisites

- Python 3.10+
- Neo4j 5.x
- Qdrant (Docker recommended)

### 1. Clone and Setup

```bash
git clone <your-repo>
cd Explore_RAG

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### 2. Start Databases

**Neo4j (Docker):**
```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:latest
```

**Qdrant (Docker):**
```bash
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  qdrant/qdrant:latest
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

Required API keys:
- `OPENAI_API_KEY` (GPT-4o for LLM, vision, and embeddings)

## 🚀 Quick Start

### Option 1: Python API

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

# Create Qdrant collection
qdrant.create_collection(
    dense_dim=encoder_manager.get_dense_dim(),
    recreate=False
)

# Ingest a 10-K PDF
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

# Query the system
hybrid_retriever = HybridRetriever(qdrant, encoder_manager)
rag_generator = RAGGenerator()

search_results = hybrid_retriever.search(
    query="What are Apple's main revenue sources?",
    top_k=10
)

answer = rag_generator.generate(
    query="What are Apple's main revenue sources?",
    search_results=search_results
)

print(answer["answer"])
```

### Option 2: REST API

**Start the server:**
```bash
python src/api/server.py
```

**Ingest a document:**
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "data/raw/apple_10k_2024.pdf",
    "ticker": "AAPL",
    "filing_date": "2024-10-31",
    "fiscal_year": 2024
  }'
```

**Query:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are Apple'\''s main revenue sources?",
    "top_k": 10,
    "strategy": "adaptive"
  }'
```

## 📊 Example Queries

The system handles various query types with adaptive strategy selection:

### Keyword-Heavy Queries (Sparse-dominant)
```
"Find all mentions of NVDA in 10-K filings"
"What is the exact EPS for Apple Q4 2024?"
"Show me Item 1A Risk Factors"
```

### Semantic Queries (Dense-dominant)
```
"What are the main risks facing semiconductor companies?"
"Explain Apple's competitive advantages"
"Summarize the business strategy from latest 10-K"
```

### Analytical Queries (ColBERT-dominant)
```
"Compare R&D spending between Apple and Microsoft"
"Analyze the relationship between revenue growth and market share"
"How do tech companies' business models differ?"
```

### Multimodal Queries
```
"Show me revenue trend charts from tech companies"
"Extract data from quarterly revenue breakdown tables"
"Find organizational structure diagrams"
```

## 🧪 Testing

Run tests:
```bash
# All tests
pytest

# Specific test file
pytest tests/test_extraction.py

# Skip slow tests
pytest -m "not slow"

# With coverage
pytest --cov=src tests/
```

## 📁 Project Structure

```
Explore_RAG/
├── src/
│   ├── extraction/          # PDF extraction
│   ├── ontology/           # Entity/relationship extraction
│   ├── embeddings/         # Multi-vector embeddings
│   ├── databases/          # Neo4j + Qdrant managers
│   ├── retrieval/          # Hybrid search
│   ├── generation/         # RAG generation
│   ├── ingestion/          # Pipeline orchestration
│   └── api/                # FastAPI server
├── config/                 # YAML configurations
├── data/                   # Data directories
│   ├── raw/               # Input PDFs
│   ├── extracted/         # Extracted content
│   └── processed/         # Processed data
├── tests/                  # Unit tests
├── examples/              # Usage examples
├── requirements.txt       # Dependencies
└── README.md
```

## ⚙️ Configuration

### Extraction Configuration (`config/extraction_config.yaml`)
- Text chunking parameters
- Table extraction settings
- Image filtering rules
- Vision API configuration

### Model Configuration (`config/model_config.yaml`)
- Dense embedding model (Voyage/OpenAI)
- Sparse embedding model (SPLADE)
- ColBERT configuration
- LLM settings (Claude)
- NER patterns

### Database Configuration
- Neo4j: `config/neo4j_config.yaml`
- Qdrant: `config/qdrant_config.yaml`

## 🎯 Performance Optimization Tips

### Extraction
- Process PDFs in parallel with `max_workers`
- Cache extracted images
- Use lazy loading for Vision API

### Embedding
- Batch process with optimal batch sizes
- Enable embedding caching
- Consider quantization for ColBERT

### Databases
- Create appropriate indexes in Neo4j
- Tune Qdrant HNSW parameters
- Use connection pooling
- Implement query result caching

### Retrieval
- Cache query embeddings
- Execute searches in parallel (asyncio)
- Use early stopping in fusion when results stabilize

## 📚 API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Main Endpoints

- `POST /query` - Query the system
- `POST /ingest` - Ingest a 10-K PDF
- `POST /ingest/upload` - Upload and ingest
- `GET /entities` - Get extracted entities
- `GET /companies/{ticker}` - Get company overview
- `GET /health` - Health check

## 🔧 Troubleshooting

### Common Issues

**1. Neo4j Connection Error**
```
Solution: Check Neo4j is running and credentials in .env are correct
```

**2. Qdrant Collection Error**
```
Solution: Delete and recreate collection with correct dimensions
```

**3. Out of Memory (ColBERT)**
```
Solution: Use quantization or reduce batch size in config
```

**4. Slow Ingestion**
```
Solution: Disable Vision API for images or reduce batch processing
```

## 🛣️ Roadmap

- [ ] Add support for 10-Q and 8-K filings
- [ ] Implement comparative analysis across multiple filings
- [ ] Add time-series analysis for financial metrics
- [ ] Support for more document types (earnings calls, presentations)
- [ ] Web UI for easier interaction
- [ ] Enhanced chart data extraction
- [ ] Multi-language support
- [ ] Cloud deployment templates

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- OpenAI GPT-4o for LLM, Vision, and Embeddings
- Neo4j for graph database
- Qdrant for vector search
- spaCy for NER
- The open-source community

## 📧 Contact

For questions or issues, please open a GitHub issue.

---

**Built with ❤️ for financial document analysis**
