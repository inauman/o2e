#!/bin/bash
# Development script for running backend and frontend together

# Start backend
cd backend && python app.py &
BACKEND_PID=$!

# Start frontend
cd ../frontend && npm start &
FRONTEND_PID=$!

# Handle shutdown
function cleanup {
  echo "Shutting down backend and frontend..."
  kill $BACKEND_PID
  kill $FRONTEND_PID
  exit 0
}

trap cleanup SIGINT
wait 