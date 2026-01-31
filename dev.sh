#!/bin/bash
# Development script - Starts both backend and frontend
# Usage: ./dev.sh

echo "Starting Medical Insight Engine in development mode..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Start backend
echo -e "${BLUE}Starting Backend on port 8000...${NC}"
cd backend
source venv/bin/activate || . venv/Scripts/activate
python -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo -e "${BLUE}Starting Frontend on port 5173...${NC}"
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Both services are running!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Frontend:  http://localhost:5173"
echo "Backend:   http://localhost:8000"
echo "API Docs:  http://localhost:8000/api/docs"
echo ""
echo "Press Ctrl+C to stop both services..."
echo ""

# Handle Ctrl+C to stop both
trap "kill $BACKEND_PID $FRONTEND_PID" INT
wait
