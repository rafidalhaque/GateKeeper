#!/bin/bash
# Celery Worker Startup Script for GateKeeper
# This script starts the Celery worker for background task processing

echo "========================================"
echo "  GateKeeper Celery Worker"
echo "========================================"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -f ".venv/bin/activate" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run: python3 -m venv .venv"
    echo "Then install requirements: .venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Check if Redis is running
echo "Checking Redis connection..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo ""
    echo "WARNING: Redis is not responding!"
    echo "Please start Redis first:"
    echo "  - redis-server"
    echo "  - or: docker run -d -p 6379:6379 redis:alpine"
    echo ""
    exit 1
fi
echo "Redis is running!"
echo ""

# Start Celery worker
echo "Starting Celery worker..."
echo "Press Ctrl+C to stop"
echo ""
celery -A celery_worker.celery worker --loglevel=info

