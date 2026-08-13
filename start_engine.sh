#!/bin/bash

echo "========================================"
echo "🚀 STARTING APEX-ICT COMMAND CENTER 🚀"
echo "========================================"

# 1. Check if Ollama is running (Required for Intent Agent)
if ! pgrep -x "ollama" > /dev/null
then
    echo "⚠️  Ollama is not running! Please open the Ollama app on your Mac."
    exit 1
fi

# 2. Start the Python FastAPI Backend in the background
echo "🟢 Starting Python FastAPI Backend (Port 8000)..."
source .venv/bin/activate
uvicorn apexict.api.main:app --reload --port 8000 &
BACKEND_PID=$!

# 3. Start the Next.js Frontend
echo "🟢 Starting Next.js Frontend (Port 3000)..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo "========================================"
echo "✅ ALL SYSTEMS GO!"
echo "🌐 Open your browser to: http://localhost:3000"
echo "🛑 Press [CTRL+C] to shut down the engine."
echo "========================================"

# Wait for user to press Ctrl+C, then kill both servers cleanly
trap "echo '\n🛑 Shutting down Apex-ICT...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait