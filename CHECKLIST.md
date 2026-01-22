# 🚀 System Setup & Verification Checklist

Use this checklist to ensure everything is set up correctly.

## Prerequisites

### Required Software
- [ ] Python 3.10 or higher installed
- [ ] Node.js 18 or higher installed
- [ ] npm installed (comes with Node.js)
- [ ] Docker installed
- [ ] Docker Compose installed
- [ ] Git installed

### Verify Installations
```bash
python --version      # Should show 3.10+
node --version        # Should show 18+
npm --version         # Should show 9+
docker --version      # Should show 20+
docker-compose --version
```

## Backend Setup

### 1. Python Environment
- [ ] Created virtual environment: `python -m venv venv`
- [ ] Activated venv: `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
- [ ] Installed dependencies: `pip install -r requirements.txt`
- [ ] Downloaded spaCy model: `python -m spacy download en_core_web_sm`

### 2. Environment Variables
- [ ] Created `.env` file in project root
- [ ] Added `OPENAI_API_KEY=sk-...`
- [ ] Added `NEO4J_PASSWORD=your_password`
- [ ] Verified `.env` is in `.gitignore`

### 3. Database Setup
- [ ] Started Neo4j: `docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/your_password neo4j:latest`
- [ ] Started Qdrant: `docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest`
- [ ] Verified Neo4j at http://localhost:7474 (user: neo4j, password: your_password)
- [ ] Verified Qdrant at http://localhost:6333/dashboard

### 4. Backend API
- [ ] Can run: `python src/api/server.py`
- [ ] Server starts without errors
- [ ] Can access: http://localhost:8000
- [ ] Can access API docs: http://localhost:8000/docs
- [ ] Health check returns `{"status": "healthy"}`: http://localhost:8000/health

## Frontend Setup

### 1. Dependencies
- [ ] Navigated to frontend: `cd frontend`
- [ ] Installed dependencies: `npm install`
- [ ] No installation errors
- [ ] `node_modules` folder created

### 2. Development Server
- [ ] Can run: `npm run dev`
- [ ] Server starts without errors
- [ ] Can access: http://localhost:3000
- [ ] Page loads correctly
- [ ] No console errors in browser

### 3. UI Verification
- [ ] Home page displays
- [ ] Navigation menu works
- [ ] Connection indicator shows green
- [ ] All 6 pages load (Home, Query, Ingest, Entities, Company, About)
- [ ] Styling looks correct (Tailwind CSS applied)

## Feature Testing

### Document Ingestion
- [ ] Navigate to http://localhost:3000/ingest
- [ ] Can drag-and-drop a PDF
- [ ] Can select a PDF via button
- [ ] Ticker field accepts input (auto-uppercase)
- [ ] Fiscal year field accepts numbers
- [ ] Filing date picker works
- [ ] Submit button becomes disabled while processing
- [ ] Success message displays with statistics
- [ ] Document ID shown after ingestion

**Test Documents**: Use the included Meta 10-K files:
- `data/raw/meta_10k_2022.pdf`
- `data/raw/meta_10k_2023.pdf`
- `data/raw/meta-10k_2024.pdf`

### Query System
- [ ] Navigate to http://localhost:3000/query
- [ ] Can type a question
- [ ] Example queries populate the text field when clicked
- [ ] Filters work (ticker, year, section)
- [ ] Advanced options expand
- [ ] Top K slider works
- [ ] Strategy dropdown works
- [ ] Search button triggers query
- [ ] Loading spinner shows while searching
- [ ] Answer displays with markdown formatting
- [ ] Sources are listed
- [ ] Context preview is available (expandable)
- [ ] Usage stats shown

**Test Queries**:
1. "What are Meta's main revenue sources?"
2. "How has revenue changed over the years?"
3. "What are the key risk factors?"
4. "Who are the key executives?"
5. "Show me financial metrics"

### Entity Browser
- [ ] Navigate to http://localhost:3000/entities
- [ ] Entities load and display
- [ ] Entity type filter works
- [ ] Limit slider affects results
- [ ] Entity cards display correctly
- [ ] Company entities are clickable
- [ ] Click navigates to company page

### Company Details
- [ ] Navigate to http://localhost:3000/company/META
- [ ] Company info loads
- [ ] Company name and ticker display
- [ ] Financial metrics section shows (if data exists)
- [ ] Executive section shows (if data exists)
- [ ] Subsidiaries section shows (if data exists)

### About Page
- [ ] Navigate to http://localhost:3000/about
- [ ] All sections render
- [ ] Architecture cards display
- [ ] Tech stack sections show
- [ ] Pipeline flow is visible
- [ ] Performance stats display

## API Endpoint Testing

Using http://localhost:8000/docs (Swagger UI):

### Health Check
- [ ] GET `/health` returns 200
- [ ] Response: `{"status": "healthy"}`

### Query
- [ ] POST `/query` accepts request
- [ ] Can test with query: "What is the revenue?"
- [ ] Returns answer, sources, context
- [ ] Filters work (ticker, fiscal_year)

### Ingest
- [ ] POST `/ingest/upload` accepts file
- [ ] Can upload a PDF
- [ ] Returns document_id and stats
- [ ] Processing completes successfully

### Entities
- [ ] GET `/entities` returns list
- [ ] Can filter by entity_type
- [ ] Can set limit parameter
- [ ] Returns array of entities

### Company
- [ ] GET `/companies/{ticker}` returns data
- [ ] Test with ticker: META
- [ ] Returns company info, metrics, executives

## Database Verification

### Neo4j
- [ ] Open http://localhost:7474
- [ ] Login successful (neo4j / your_password)
- [ ] Run query: `MATCH (n) RETURN count(n)`
- [ ] Should show number of nodes after ingestion
- [ ] Run query: `MATCH (c:Company) RETURN c.name, c.ticker LIMIT 5`
- [ ] Should show ingested companies

### Qdrant
- [ ] Open http://localhost:6333/dashboard
- [ ] Collection `financial_documents` exists
- [ ] Collection shows vectors after ingestion
- [ ] Check collection size
- [ ] Verify multi-vector setup (dense, sparse, colbert)

## Performance Tests

### Backend
- [ ] API responds within 1 second for health check
- [ ] Query responds within 5-10 seconds
- [ ] Ingestion completes within 2-10 minutes (depending on PDF size)
- [ ] No memory leaks (monitor during operation)

### Frontend
- [ ] Page loads within 2 seconds
- [ ] Navigation is instant
- [ ] No console errors
- [ ] No console warnings
- [ ] Responsive on mobile (test with browser dev tools)
- [ ] Works in Chrome
- [ ] Works in Firefox
- [ ] Works in Safari (if on Mac)

## Integration Tests

### Full Workflow Test
1. [ ] Start both backend and frontend
2. [ ] Upload a 10-K document (use Meta 2024)
3. [ ] Wait for processing to complete
4. [ ] Verify success statistics
5. [ ] Navigate to Query page
6. [ ] Ask: "What was Meta's revenue in 2024?"
7. [ ] Verify answer includes revenue figures
8. [ ] Check sources include document references
9. [ ] Navigate to Entities page
10. [ ] Find "Meta" or "META" company entity
11. [ ] Click to view company details
12. [ ] Verify metrics and information display

### Multi-Year Analysis Test
1. [ ] Upload Meta 2022 10-K (ticker: META, year: 2022)
2. [ ] Upload Meta 2023 10-K (ticker: META, year: 2023)
3. [ ] Upload Meta 2024 10-K (ticker: META, year: 2024)
4. [ ] Query: "How has Meta's revenue changed from 2022 to 2024?"
5. [ ] Verify answer includes multi-year comparison
6. [ ] Verify sources from multiple years
7. [ ] Check entities from all three years appear

## Error Handling Tests

### Backend Errors
- [ ] Test invalid API endpoint: GET `/invalid` returns 404
- [ ] Test query without backend running shows connection error
- [ ] Test ingestion with invalid PDF shows error message
- [ ] Test query with empty string shows validation error

### Frontend Errors
- [ ] Backend offline shows "Disconnected" status
- [ ] Invalid file upload shows error message
- [ ] Empty query submission prevented
- [ ] Network errors display user-friendly messages

## Security Checks

- [ ] `.env` file not committed to Git
- [ ] API keys not visible in frontend code
- [ ] No console.log of sensitive data
- [ ] CORS configured correctly
- [ ] File uploads validated (PDF only)
- [ ] Input sanitization working

## Documentation Verification

- [ ] README.md is complete and accurate
- [ ] QUICKSTART.md works for new users
- [ ] FRONTEND_SETUP.md has correct commands
- [ ] ARCHITECTURE.md diagrams are clear
- [ ] API documentation at /docs is complete
- [ ] Code comments are present and helpful

## Deployment Readiness

### Production Checklist
- [ ] All tests pass
- [ ] No errors in logs
- [ ] Environment variables properly configured
- [ ] Database backups configured (if needed)
- [ ] HTTPS configured (for production)
- [ ] API rate limiting considered
- [ ] Monitoring set up (optional)
- [ ] Error tracking configured (optional)

### Docker Deployment (Optional)
- [ ] Docker Compose file tested
- [ ] All containers start successfully
- [ ] Services can communicate
- [ ] Data persists across restarts
- [ ] Volumes configured for Neo4j and Qdrant

## Troubleshooting Verification

If any item fails, consult:
1. **Backend issues**: Check backend terminal logs
2. **Frontend issues**: Check browser console
3. **Database issues**: Verify Docker containers running
4. **API issues**: Check /docs endpoint
5. **Connection issues**: Verify ports not in use
6. **Import errors**: Reinstall dependencies

## Common Issues & Solutions

### Issue: "Module not found"
- [ ] Virtual environment activated?
- [ ] Dependencies installed?
- [ ] Correct Python version?

### Issue: "Connection refused" 
- [ ] Backend running?
- [ ] Correct port (8000)?
- [ ] Firewall blocking?

### Issue: "Cannot connect to Neo4j"
- [ ] Docker container running?
- [ ] Password correct in .env?
- [ ] Port 7687 not in use?

### Issue: "Frontend shows disconnected"
- [ ] Backend health check responding?
- [ ] CORS configured?
- [ ] Proxy settings in vite.config.js?

### Issue: "Styles not loading"
- [ ] Tailwind CSS configured?
- [ ] PostCSS running?
- [ ] Clear browser cache?

## Final Verification

After completing all above:
- [ ] Run `./start_dev.sh` (or `start_dev.bat` on Windows)
- [ ] Both servers start without errors
- [ ] Can complete full workflow (upload → query → browse)
- [ ] No errors in any logs
- [ ] System feels responsive
- [ ] Ready for production use! 🚀

## Sign Off

- [ ] Backend setup complete ✅
- [ ] Frontend setup complete ✅
- [ ] Databases configured ✅
- [ ] All features tested ✅
- [ ] Documentation reviewed ✅
- [ ] Ready to use! ✅

---

**Date Completed**: _______________

**Tested By**: _______________

**Notes**: _______________________________________________
