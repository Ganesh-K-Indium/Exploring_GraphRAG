# 🚀 Getting Started - 5 Minute Quick Start

This guide will get you up and running in 5 minutes!

## Prerequisites

✅ Python 3.10+
✅ Node.js 18+
✅ Docker & Docker Compose
✅ OpenAI API key

## Step 1: Clone & Install (2 minutes)

```bash
# Navigate to project
cd Explore_RAG

# Install Python dependencies
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Install Frontend dependencies
cd frontend
npm install
cd ..
```

## Step 2: Configure Environment (1 minute)

Create `.env` file in project root:

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

## Step 3: Start Databases (1 minute)

```bash
# Start Neo4j
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:latest

# Start Qdrant
docker run -d --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  qdrant/qdrant:latest
```

## Step 4: Start the System (1 minute)

### Option A: Quick Start Script (Recommended)

```bash
# Mac/Linux
./start_dev.sh

# Windows
start_dev.bat
```

This automatically starts both backend and frontend!

### Option B: Manual Start

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
python src/api/server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Step 5: Access the UI

Open your browser to: **http://localhost:3000**

You should see:
✅ Beautiful home page
✅ Green "Connected" indicator
✅ Navigation menu with 6 pages

## First Steps

### 1. Upload a Document (2 minutes)

1. Click **"Ingest"** in the navigation
2. Drag & drop a PDF (or use the included Meta 10-K files in `data/raw/`)
3. Enter metadata:
   - **Ticker**: META
   - **Fiscal Year**: 2024
4. Click **"Upload and Ingest"**
5. Wait for processing (2-5 minutes)
6. See success statistics!

### 2. Query the System (1 minute)

1. Click **"Query"** in the navigation
2. Type a question: "What was Meta's revenue in 2024?"
3. Click **"Search"**
4. See the answer with citations!

### 3. Browse Entities (30 seconds)

1. Click **"Entities"** in the navigation
2. Filter by type (Company, Person, etc.)
3. Click on a company to see details

### 4. Explore Company Details (30 seconds)

1. Click **"Company"** or click a company from Entities
2. View financial metrics
3. See executive team
4. Browse subsidiaries

## What Just Happened?

Behind the scenes, the system:

1. **Extracted** text, tables, images, and charts from the PDF
2. **Identified** entities (companies, people, metrics, risks)
3. **Created** relationships in Neo4j knowledge graph
4. **Generated** multi-vector embeddings (dense, sparse, ColBERT)
5. **Stored** everything in Neo4j + Qdrant
6. **Retrieved** relevant context using hybrid search
7. **Generated** answer using GPT-4o

## System URLs

Once running, you can access:

- 🎨 **Frontend UI**: http://localhost:3000
- 🔌 **Backend API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs
- 📈 **Neo4j Browser**: http://localhost:7474 (neo4j/your_password)
- 🔍 **Qdrant Dashboard**: http://localhost:6333/dashboard

## Example Queries to Try

Once you've ingested a document, try these:

### Financial Queries
- "What was the total revenue?"
- "How has revenue changed over the past 3 years?"
- "What are the main revenue sources?"
- "Show me the profit margins"

### Risk Analysis
- "What are the key risk factors?"
- "What regulatory risks does the company face?"
- "What are the competitive threats?"

### Company Information
- "Who are the key executives?"
- "What subsidiaries does the company own?"
- "Where are the main offices located?"

### Comparative Queries (after ingesting multiple years)
- "Compare revenue between 2022 and 2024"
- "How has R&D spending changed?"
- "What are the year-over-year trends?"

## Advanced Features

### Multi-Year Analysis

Ingest multiple years of 10-K documents:

```bash
# Upload each year separately
1. Upload: meta_10k_2022.pdf (Ticker: META, Year: 2022)
2. Upload: meta_10k_2023.pdf (Ticker: META, Year: 2023)
3. Upload: meta-10k_2024.pdf (Ticker: META, Year: 2024)

# Then query across years
"How has Meta's business evolved from 2022 to 2024?"
```

### Advanced Search Options

On the Query page, expand "Advanced Options":

- **Top K**: Adjust number of results (5-30)
- **Strategy**: 
  - Adaptive (recommended) - automatically chooses best strategy
  - RRF - Reciprocal Rank Fusion
  - Weighted - Weighted fusion of vectors

### Filters

Narrow down your search:

- **Ticker**: Search only specific company (e.g., META, AAPL)
- **Fiscal Year**: Search specific year (e.g., 2024)
- **Section**: Search specific 10-K section (e.g., Item 1A - Risk Factors)

## Troubleshooting

### Backend won't start?
```bash
# Check virtual environment is activated
source venv/bin/activate

# Check dependencies installed
pip install -r requirements.txt

# Check .env file exists
ls -la .env
```

### Frontend won't start?
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Database connection errors?
```bash
# Check Docker containers are running
docker ps

# Restart containers
docker restart neo4j qdrant

# Check logs
docker logs neo4j
docker logs qdrant
```

### "Cannot connect to Neo4j"?
- Verify password in `.env` matches Docker command
- Check port 7687 is not in use
- Try: `docker restart neo4j`

### Frontend shows "Disconnected"?
- Ensure backend is running on port 8000
- Check browser console for errors
- Try: http://localhost:8000/health directly

## Next Steps

### Learn More
- 📖 Read `README.md` for complete documentation
- 📚 Check `FRONTEND_SETUP.md` for UI details
- 🏗️ Review `ARCHITECTURE.md` for system design
- ✅ Use `CHECKLIST.md` to verify setup

### Explore Examples
```bash
# Python examples
python examples/simple_usage.py
python examples/multi_year_analysis.py

# API examples
python examples/api_usage.py
```

### Deploy to Production
- See `README.md` deployment section
- Consider using Docker Compose
- Set up monitoring and backups
- Configure HTTPS for production

## Getting Help

### Check Documentation
1. `README.md` - Complete system documentation
2. `FRONTEND_SETUP.md` - Frontend guide
3. `QUICKSTART.md` - Backend quick start
4. `HISTORICAL_ANALYSIS_GUIDE.md` - Multi-year analysis

### Check Logs
- Backend: Terminal where `server.py` is running
- Frontend: Browser console (F12)
- Neo4j: `docker logs neo4j`
- Qdrant: `docker logs qdrant`

### Common Issues
- Port already in use? Change ports in configs
- Out of memory? Reduce batch sizes in configs
- API rate limits? Add delays or increase limits

## Performance Tips

### For Faster Ingestion
- Use PDF files directly from SEC EDGAR
- Process documents one at a time
- Ensure good internet connection for API calls

### For Faster Queries
- Use specific filters (ticker, year)
- Start with lower top_k values (10 instead of 30)
- Use "Adaptive" strategy for best automatic performance

### For Better Results
- Provide accurate metadata (ticker, year, date)
- Use clear, specific questions
- Reference the document structure (e.g., "in the risk factors section")

## Summary

You now have a complete Multimodal Graph RAG system running! 🎉

✅ Frontend UI for easy interaction
✅ Backend API with all features
✅ Neo4j graph database for relationships
✅ Qdrant vector database for semantic search
✅ Multi-vector embeddings for optimal retrieval
✅ GPT-4o for intelligent answers

**Start exploring your financial documents with AI-powered analysis!**

## Quick Reference Card

```
┌─────────────────────────────────────────┐
│         QUICK REFERENCE                 │
├─────────────────────────────────────────┤
│ Frontend:    http://localhost:3000     │
│ Backend:     http://localhost:8000     │
│ API Docs:    /docs                      │
│ Neo4j:       http://localhost:7474     │
│ Qdrant:      http://localhost:6333     │
├─────────────────────────────────────────┤
│ Start:       ./start_dev.sh            │
│ Stop:        Ctrl+C                     │
├─────────────────────────────────────────┤
│ Upload:      /ingest page               │
│ Query:       /query page                │
│ Browse:      /entities page             │
└─────────────────────────────────────────┘
```

Happy analyzing! 📊✨
