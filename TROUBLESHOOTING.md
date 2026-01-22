# Troubleshooting Guide

## Common Issues and Solutions

### 1. Hugging Face Cache Permission Error

**Error:**
```
OSError: PermissionError at /Users/I8798/.cache/huggingface when downloading naver/splade-cocondenser-ensembledistil
```

**Solution A: Quick Fix Script**
```bash
./fix_huggingface_cache.sh
```

**Solution B: Manual Fix**
```bash
# Remove lock files
find ~/.cache/huggingface -name "*.lock" -delete

# Fix permissions
chmod -R u+w ~/.cache/huggingface

# Create cache directory
mkdir -p ~/.cache/huggingface/hub
```

**Solution C: Clear Cache Completely**
```bash
# Remove entire cache (models will re-download)
rm -rf ~/.cache/huggingface

# Recreate directory
mkdir -p ~/.cache/huggingface/hub
```

**Solution D: Use Custom Cache Location**
```bash
# Set custom cache in .env
export HF_HOME=/Users/I8798/Desktop/Explore_RAG/.cache/huggingface
mkdir -p $HF_HOME
```

Then add to `.env`:
```bash
HF_HOME=/Users/I8798/Desktop/Explore_RAG/.cache/huggingface
```

---

### 2. Module Not Found Error

**Error:**
```
ModuleNotFoundError: No module named 'src'
```

**Solution:**
```bash
# Use the launcher script
python run_server.py

# OR use module syntax
python -m src.api.server

# OR use the startup script
./start_dev.sh
```

**Don't do this:**
```bash
python src/api/server.py  # ❌ Will fail
```

---

### 3. Port Already in Use

**Error:**
```
Error: [Errno 48] Address already in use
```

**Solution (Mac/Linux):**
```bash
# Find process on port 8000
lsof -ti:8000

# Kill it
lsof -ti:8000 | xargs kill -9

# Or for port 3000 (frontend)
lsof -ti:3000 | xargs kill -9
```

**Solution (Windows):**
```cmd
# Find process
netstat -ano | findstr :8000

# Kill it (replace PID with actual number)
taskkill /PID <PID> /F
```

---

### 4. Neo4j Connection Error

**Error:**
```
Could not connect to Neo4j at bolt://localhost:7687
```

**Solution:**
```bash
# Check if Neo4j is running
docker ps | grep neo4j

# If not running, start it
docker start neo4j

# Or create new instance
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:latest

# Verify it's running
curl http://localhost:7474
```

**Check password in .env matches:**
```bash
# .env file should have
NEO4J_PASSWORD=your_password
```

---

### 5. Qdrant Connection Error

**Error:**
```
Could not connect to Qdrant at localhost:6333
```

**Solution:**
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# If not running, start it
docker start qdrant

# Or create new instance
docker run -d --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  qdrant/qdrant:latest

# Verify it's running
curl http://localhost:6333
```

---

### 6. OpenAI API Key Error

**Error:**
```
AuthenticationError: Incorrect API key provided
```

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Check it has the key
grep OPENAI_API_KEY .env

# Set the key
echo "OPENAI_API_KEY=sk-your-actual-key" >> .env

# Verify format (should start with sk-)
cat .env | grep OPENAI
```

---

### 7. Frontend Shows "Disconnected"

**Issue:** Red indicator in header

**Solution:**
```bash
# 1. Check backend is running
curl http://localhost:8000/health

# 2. Check backend logs for errors
# Look at terminal where backend is running

# 3. Check browser console
# Open DevTools (F12) and look for errors

# 4. Restart backend
# Kill backend process (Ctrl+C)
python run_server.py

# 5. Restart frontend
cd frontend
npm run dev
```

---

### 8. Dependencies Not Found

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Ensure venv is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

---

### 9. Frontend Build Errors

**Error:**
```
npm ERR! code ELIFECYCLE
```

**Solution:**
```bash
cd frontend

# Clear cache
rm -rf node_modules package-lock.json .vite

# Reinstall
npm install

# Try again
npm run dev
```

---

### 10. Model Download Slow/Stuck

**Issue:** SPLADE or ColBERT model download hangs

**Solution:**
```bash
# Pre-download models manually
python << 'EOF'
from transformers import AutoModelForMaskedLM, AutoTokenizer

# Download SPLADE
print("Downloading SPLADE...")
model = AutoModelForMaskedLM.from_pretrained("naver/splade-cocondenser-ensembledistil")
tokenizer = AutoTokenizer.from_pretrained("naver/splade-cocondenser-ensembledistil")
print("✅ SPLADE downloaded")

# Download ColBERT (if using)
print("Downloading ColBERT...")
from colbert import Indexer
print("✅ ColBERT ready")
EOF
```

---

### 11. Out of Memory Error

**Error:**
```
RuntimeError: CUDA out of memory
```

**Solution:**
```bash
# Reduce batch sizes in config/model_config.yaml
batch_size: 8  # Reduce from 32 to 8

# Or disable ColBERT (most memory-intensive)
# Comment out ColBERT embedder initialization

# Or use CPU only (add to .env)
CUDA_VISIBLE_DEVICES=-1
```

---

### 12. Docker Container Won't Start

**Error:**
```
Error response from daemon: Conflict. The container name "/neo4j" is already in use
```

**Solution:**
```bash
# Remove existing container
docker rm -f neo4j
docker rm -f qdrant

# Start fresh
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:latest

docker run -d --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  qdrant/qdrant:latest
```

---

### 13. PDF Upload Fails

**Error:**
```
Error: File upload failed
```

**Solution:**
```bash
# Check file size (must be < 50MB)
ls -lh your_file.pdf

# Check file type (must be PDF)
file your_file.pdf

# Check backend logs for specific error

# Try with a smaller test file first
```

---

### 14. Query Returns No Results

**Issue:** Search returns empty results

**Solution:**
```bash
# 1. Verify documents are ingested
curl http://localhost:8000/entities | jq

# 2. Check Qdrant has vectors
curl http://localhost:6333/collections/financial_documents

# 3. Try re-ingesting the document

# 4. Check query filters aren't too restrictive
# Remove ticker/year filters and try again

# 5. Check backend logs for errors
```

---

### 15. Startup Script Fails

**Error:**
```
./start_dev.sh: Permission denied
```

**Solution:**
```bash
# Make script executable
chmod +x start_dev.sh
chmod +x fix_huggingface_cache.sh

# Then run
./start_dev.sh
```

---

## Quick Diagnostic Commands

### Check All Services
```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# Neo4j
curl http://localhost:7474

# Qdrant
curl http://localhost:6333
```

### Check Docker Containers
```bash
docker ps -a
```

### Check Python Environment
```bash
which python
python --version
pip list
```

### Check Node Environment
```bash
which node
node --version
npm --version
```

### Check Logs
```bash
# Backend logs
tail -f logs/api.log

# Docker logs
docker logs neo4j
docker logs qdrant
```

---

## Reset Everything (Nuclear Option)

If nothing works, start fresh:

```bash
# 1. Stop all processes
killall python
killall node

# 2. Remove Docker containers
docker rm -f neo4j qdrant

# 3. Clean Python
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 4. Clean Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
cd ..

# 5. Clean cache
rm -rf ~/.cache/huggingface
mkdir -p ~/.cache/huggingface/hub

# 6. Restart databases
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:latest

docker run -d --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  qdrant/qdrant:latest

# 7. Update .env
echo "OPENAI_API_KEY=sk-your-key" > .env
echo "NEO4J_PASSWORD=password123" >> .env

# 8. Start everything
./start_dev.sh
```

---

## Getting Help

If you're still stuck:

1. **Check the logs** - Most errors are logged with details
2. **Check GitHub Issues** - Someone may have had the same problem
3. **Check documentation** - README.md, GETTING_STARTED.md
4. **Try the examples** - Run example scripts to verify setup

---

## Prevention Tips

1. **Always activate venv** before running Python
2. **Check Docker is running** before starting services
3. **Keep API keys secure** - Never commit .env to Git
4. **Monitor disk space** - Models and vectors take space
5. **Update dependencies regularly** - `pip install --upgrade -r requirements.txt`
