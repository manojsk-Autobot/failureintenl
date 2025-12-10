#!/bin/bash
# Quick deployment script for Database Monitor & AI Analysis Service

echo "🚀 Database Monitor & AI Analysis Service - Deployment"
echo "========================================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found"
    if [ -f ".env.example" ]; then
        echo "📝 Creating .env from .env.example"
        cp .env.example .env
        echo "⚠️  Please edit .env with your credentials before running the service"
        exit 1
    else
        echo "❌ No .env.example found. Please create .env manually"
        exit 1
    fi
fi

echo "✅ Found .env file"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Run tests
echo ""
echo "🧪 Running quick tests..."
python3 -c "import sys; sys.path.insert(0, '.'); from llm.factory import LLMFactory; print('✅ LLM module OK')" 2>/dev/null
python3 -c "import sys; sys.path.insert(0, '.'); from db import MSSQLConnector; print('✅ DB module OK')" 2>/dev/null
python3 -c "import sys; sys.path.insert(0, '.'); from services import EmailService; print('✅ Services module OK')" 2>/dev/null

# Start the service
echo ""
echo "🎯 Starting the service..."
echo ""

# Check if port 8000 is already in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port 8000 is already in use. Stopping existing process..."
    pkill -f "python3 run.py"
    sleep 2
fi

# Start the service
nohup python3 run.py > server.log 2>&1 &
PID=$!

# Wait for service to start
sleep 3

# Check if service is running
if ps -p $PID > /dev/null; then
    echo "✅ Service started successfully (PID: $PID)"
    echo ""
    echo "📚 Documentation: http://localhost:8000/docs"
    echo "🏥 Health Check:  http://localhost:8000/health"
    echo "📊 API Root:      http://localhost:8000/"
    echo ""
    echo "📝 Logs: tail -f server.log"
    echo "🛑 Stop: pkill -f 'python3 run.py'"
    echo ""
    
    # Test the service
    echo "🔍 Testing service..."
    RESPONSE=$(curl -s http://localhost:8000/health 2>/dev/null)
    if [ ! -z "$RESPONSE" ]; then
        echo "✅ Service is responding"
        echo ""
        echo "🎉 Deployment successful!"
    else
        echo "⚠️  Service started but not responding yet. Check server.log"
    fi
else
    echo "❌ Failed to start service. Check server.log for errors"
    tail -20 server.log
    exit 1
fi
