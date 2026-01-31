#!/bin/bash
# Setup script for Medical Insight Engine
# Run this script to set up the entire project

set -e

echo "================================"
echo "Medical Insight Engine Setup"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.9+${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm is not installed. Please install Node.js 16+${NC}"
    exit 1
fi

if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}PostgreSQL not found. Using Docker PostgreSQL setup...${NC}"
    if command -v docker &> /dev/null; then
        echo -e "${YELLOW}Starting PostgreSQL container...${NC}"
        docker run -d --name postgres-medical -e POSTGRES_DB=medical_insight -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15 || true
        sleep 5
    else
        echo -e "${YELLOW}Install PostgreSQL or Docker to continue${NC}"
    fi
fi

echo -e "${GREEN}Prerequisites check passed!${NC}"
echo ""

# Backend Setup
echo -e "${YELLOW}Setting up Backend...${NC}"
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate || . venv/Scripts/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download spacy model
echo "Downloading spacy models..."
python -m spacy download en_core_web_sm

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${YELLOW}Please edit backend/.env and set your database credentials${NC}"
fi

# Create logs directory
mkdir -p logs uploads

echo -e "${GREEN}Backend setup complete!${NC}"
echo ""

# Frontend Setup
echo -e "${YELLOW}Setting up Frontend...${NC}"
cd ../frontend

# Install dependencies
echo "Installing npm dependencies..."
npm install

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
fi

echo -e "${GREEN}Frontend setup complete!${NC}"
echo ""

# Final instructions
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo -e "1. ${YELLOW}Configure Backend:${NC}"
echo "   Edit backend/.env and set:"
echo "   - DATABASE_URL (PostgreSQL connection)"
echo "   - SECRET_KEY and ENCRYPTION_KEY (generate new keys)"
echo "   - CORS_ORIGINS (your frontend URL)"
echo ""
echo -e "2. ${YELLOW}Start Backend:${NC}"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python -m uvicorn app.main:app --reload --port 8000"
echo ""
echo -e "3. ${YELLOW}In another terminal, Start Frontend:${NC}"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo -e "4. ${YELLOW}Access the application:${NC}"
echo "   Frontend: http://localhost:5173"
echo "   Backend API Docs: http://localhost:8000/api/docs"
echo ""
echo -e "${GREEN}Happy coding!${NC}"
