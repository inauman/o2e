#!/bin/bash
# Development script for running backend and frontend together

# Activate virtual environment
echo "🔹 Activating virtual environment in $(pwd)"
source .venv/bin/activate

# Go to the project root directory
cd $(dirname "$0")

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
  echo "⚠️ Frontend directory not found. Only starting the backend."
  FRONTEND_MISSING=true
else
  FRONTEND_MISSING=false
fi

# Kill any process using port 5000 (common on macOS with AirPlay)
echo "🔹 Checking if port 5000 is in use..."
if command -v lsof >/dev/null 2>&1; then
  PORT_PID=$(lsof -ti:5000)
  if [ ! -z "$PORT_PID" ]; then
    echo "🔹 Killing process using port 5000 (PID: $PORT_PID)"
    kill -9 $PORT_PID
  else
    echo "🔹 Port 5000 is available"
  fi
fi

# Start backend on default port 5000
echo "🔹 Starting backend on port 5000..."
cd backend && python app.py &
BACKEND_PID=$!

# Start frontend if it exists
if [ "$FRONTEND_MISSING" = false ]; then
  echo "🔹 Starting frontend..."
  cd ../frontend && npm start &
  FRONTEND_PID=$!
fi

# Handle shutdown
function cleanup {
  echo "🔹 Shutting down services..."
  kill $BACKEND_PID 2>/dev/null
  if [ "$FRONTEND_MISSING" = false ]; then
    kill $FRONTEND_PID 2>/dev/null
  fi
  exit 0
}

trap cleanup SIGINT
wait 