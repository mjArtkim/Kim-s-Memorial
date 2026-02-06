#!/bin/bash
# Local Test Script for Kim's Memorial (Manual Mode)

set -e

echo "🚀 Starting Local Test Setup..."

# 1. Build Frontend
echo "📦 Building Frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "   - Installing frontend dependencies..."
    npm install
fi
npm run build
cd ..

# 2. Setup and Run Backend
echo "🐍 Setting up Backend..."
# Setup venv in root or backend? Script put it in backend before. 
# Let's keep venv in backend but run from root.

cd backend
if [ ! -d "venv" ]; then
    echo "   - Creating Python virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
cd .. 

# Run the application from ROOT so it sees ./data and ./photos
echo "🏃 Running Application..."
echo "----------------------------------------------"
echo "   Access at: http://localhost:7554"
echo "   Press Ctrl+C to stop"
echo "----------------------------------------------"
python backend/app.py
