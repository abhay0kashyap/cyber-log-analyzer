#!/bin/bash

# Cyber Log Analyzer - Quick Setup Script
# This script sets up the entire SIEM system

set -e  # Exit on error

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
touch logs/auth.log
print_status "Directories created"

# Setup Backend
echo ""
echo "🐍 Setting up Backend..."
cd "$(dirname "$0")"

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

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
    cd webapp
    
    # Install frontend dependencies
    npm install
    print_status "Frontend dependencies installed"
    
    # Create environment file
    if [ ! -f ".env" ]; then
        echo "REACT_APP_API_URL=http://localhost:8000" > .env
        print_status "Environment file created"
    else
        print_status "Environment file already exists"
    fi
    
    cd ..
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
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "   Terminal 2 - Frontend:"
echo "   cd webapp"
echo "   npm start"
echo ""
echo "   Dashboard: http://localhost:3000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "📖 See README.md for detailed instructions"
echo "============================================"

