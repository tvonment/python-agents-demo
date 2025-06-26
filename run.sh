#!/bin/bash

# Multi-Agent System Startup Script

echo "🚀 Starting Multi-Agent System..."
echo "=================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and configure your settings:"
    echo "cp .env.example .env"
    exit 1
fi

# Check Python dependencies
echo "📦 Checking Python dependencies..."
if ! pip show semantic-kernel >/dev/null 2>&1; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Check Node.js dependencies
echo "📦 Checking Node.js dependencies..."
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing Node.js dependencies..."
    cd frontend && npm install && cd ..
fi

echo "✅ Dependencies ready!"
echo ""

# Function to start backend
start_backend() {
    echo "🐍 Starting Python backend on http://localhost:8000"
    cd src && python main.py
}

# Function to start frontend
start_frontend() {
    echo "⚛️  Starting React frontend on http://localhost:3000"
    cd frontend && npm start
}

# Check if user wants to start both or just one
if [ "$1" = "backend" ]; then
    start_backend
elif [ "$1" = "frontend" ]; then
    start_frontend
elif [ "$1" = "demo" ]; then
    echo "🧪 Running demo script..."
    python demo.py
else
    echo "Choose what to start:"
    echo "1. Both backend and frontend"
    echo "2. Backend only"
    echo "3. Frontend only"
    echo "4. Run demo"
    read -p "Enter your choice (1-4): " choice
    
    case $choice in
        1)
            echo "Starting both services..."
            echo "Open http://localhost:3000 in your browser"
            echo "Press Ctrl+C to stop both services"
            # Start backend in background
            start_backend &
            BACKEND_PID=$!
            # Wait a moment for backend to start
            sleep 3
            # Start frontend (this will block)
            start_frontend
            # If frontend exits, kill backend
            kill $BACKEND_PID 2>/dev/null
            ;;
        2)
            start_backend
            ;;
        3)
            start_frontend
            ;;
        4)
            python demo.py
            ;;
        *)
            echo "Invalid choice"
            exit 1
            ;;
    esac
fi
