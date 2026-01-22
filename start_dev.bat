@echo off
REM Development startup script for Graph RAG system (Windows)

echo 🚀 Starting Multimodal Graph RAG System...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run: python -m venv venv
    exit /b 1
)

REM Check if node_modules exists
if not exist "frontend\node_modules" (
    echo 📦 Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
    echo ✅ Frontend dependencies installed
    echo.
)

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  Warning: .env file not found. Please create one with your API keys.
    echo.
)

REM Start backend
echo 🔧 Starting Backend API (port 8000)...
start "Backend API" cmd /k "venv\Scripts\activate && python run_server.py"
timeout /t 5 /nobreak > nul

REM Start frontend
echo 🎨 Starting Frontend UI (port 3000)...
cd frontend
start "Frontend UI" cmd /k "npm run dev"
cd ..

echo.
echo ✅ System starting up...
echo.
echo 📊 Frontend UI:     http://localhost:3000
echo 🔌 Backend API:     http://localhost:8000
echo 📚 API Docs:        http://localhost:8000/docs
echo 📈 Neo4j Browser:   http://localhost:7474
echo 🔍 Qdrant UI:       http://localhost:6333/dashboard
echo.
echo Close the terminal windows to stop the servers
echo.
