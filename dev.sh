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

# Kill any process using port 5001 (if needed)
echo "🔹 Checking if port 5001 is in use..."
PORT_PID=$(lsof -ti:5001)
if [ ! -z "$PORT_PID" ]; then
    echo "🔹 Killing process using port 5001 (PID: $PORT_PID)"
    kill -9 $PORT_PID
fi
echo "🔹 Port 5001 is available"

# Start backend on port 5001
echo "🔹 Starting backend on port 5001..."
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