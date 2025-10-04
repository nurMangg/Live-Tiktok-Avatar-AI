#!/bin/bash

# TikTok Live AI Avatar - Startup Script
# This script starts both Node.js and Python servers

echo "🚀 Starting TikTok Live AI Avatar Application..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please edit it with your API keys."
    else
        echo "❌ .env.example not found. Please create .env manually."
    fi
fi

# Install Node.js dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Install Python dependencies if needed
echo "📦 Checking Python dependencies..."
pip3 install -r requirements.txt -q

echo ""
echo "✨ Starting servers..."
echo ""

# Start Python backend in background
echo "🐍 Starting Python AI Avatar Server on port 5000..."
python3 avatar_server.py &
PYTHON_PID=$!

# Wait a bit for Python server to start
sleep 3

# Start Node.js server
echo "🟢 Starting Node.js Server on port 3000..."
node server.js &
NODE_PID=$!

echo ""
echo "✅ Servers started successfully!"
echo ""
echo "📱 Open your browser and go to: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping servers...'; kill $PYTHON_PID $NODE_PID; exit" INT

# Keep script running
wait

