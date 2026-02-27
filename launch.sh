#!/bin/bash
set -e

# Get the absolute path of the project root
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "🚀 Building frontend..."
cd "$PROJECT_ROOT/frontend"
npm install --silent
npm run build --silent

echo "✅ Frontend built."
echo "🚀 Starting backend with uv on http://localhost:8000"

# Run backend with uv from the backend directory
# Added: opencv-python-headless, langgraph
cd "$PROJECT_ROOT/backend"
uv run --with fastapi --with uvicorn --with pandas --with numpy --with openpyxl --with opencv-python-headless --with langgraph main.py
