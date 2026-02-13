#!/bin/bash

# Cyber Log Analyzer - Quick Setup Script
# This script sets up the entire SIEM system

set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "🛡️  Cyber Log Analyzer - SIEM System Setup"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

cd "$PROJECT_ROOT"

# Check Python version
echo "📋 Checking prerequisites..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_status "Python 3 found: $PYTHON_VERSION"
else
    print_error "Python 3 is required but not installed."
    exit 1
fi

if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_status "npm found: $NPM_VERSION"
else
    print_warning "npm not found. Frontend setup will be skipped."
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p reports
mkdir -p uploaded_logs
mkdir -p backend/logs
touch logs/auth.log
touch backend/logs/auth.log
print_status "Directories created"

# Setup Backend
echo ""
echo "🐍 Setting up Backend..."
VENV_DIR=".venv"

# Create virtual environment
if [ -d ".venv" ]; then
    print_status "Virtual environment already exists at .venv"
elif [ -d "venv" ]; then
    VENV_DIR="venv"
    print_warning "Using existing legacy virtual environment at ./venv"
else
    python3 -m venv .venv
    print_status "Virtual environment created at .venv"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install backend dependencies
echo ""
echo "📦 Installing backend dependencies..."
pip install --upgrade pip -q
pip install -r backend/requirements.txt -q
print_status "Backend dependencies installed"

# Setup Frontend
if command -v npm &> /dev/null; then
    echo ""
    echo "⚛️  Setting up Frontend..."
    if [ ! -d "frontend" ]; then
        print_warning "frontend/ directory not found. Skipping frontend setup."
    else
        cd frontend
    
        # Install frontend dependencies
        npm install
        print_status "Frontend dependencies installed"
    
        # Create environment file for Vite if none exists
        if [ ! -f ".env" ] && [ ! -f ".env.local" ]; then
            echo "VITE_API_URL=http://127.0.0.1:8000" > .env
            print_status "Frontend .env file created with VITE_API_URL"
        else
            print_status "Frontend env file already exists"
        fi
    
        cd ..
    fi
else
    print_warning "Frontend setup skipped (npm not found)"
fi

echo ""
echo "============================================"
echo "✅ Setup Complete!"
echo ""
echo "🚀 To start the application:"
echo ""
echo "   Terminal 1 - Backend:"
echo "   cd backend"
echo "   source $VENV_DIR/bin/activate"
echo "   uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
echo ""
echo "   Terminal 2 - Frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "   Dashboard: http://127.0.0.1:5173"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "📖 See README.md for detailed instructions"
echo "============================================"
