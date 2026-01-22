#!/bin/bash

# Development startup script for Graph RAG system

echo "🚀 Starting Multimodal Graph RAG System..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv venv"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo "✅ Frontend dependencies installed"
    echo ""
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Please create one with your API keys."
    echo ""
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo "🔧 Starting Backend API (port 8000)..."
source venv/bin/activate
python src/api/server.py &
BACKEND_PID=$!
sleep 3

# Check if backend started successfully
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend failed to start. Check logs above."
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi
echo "✅ Backend running at http://localhost:8000"
echo ""

# Start frontend
echo "🎨 Starting Frontend UI (port 3000)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
sleep 3

echo ""
echo "✅ System ready!"
echo ""
echo "📊 Frontend UI:     http://localhost:3000"
echo "🔌 Backend API:     http://localhost:8000"
echo "📚 API Docs:        http://localhost:8000/docs"
echo "📈 Neo4j Browser:   http://localhost:7474"
echo "🔍 Qdrant UI:       http://localhost:6333/dashboard"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for processes
wait
