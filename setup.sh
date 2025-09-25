#!/bin/bash

# CSE-AIML ERP System Setup Script
echo "🚀 Setting up CSE-AIML ERP System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check if MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️  MongoDB is not running. Please start MongoDB first:"
    echo "   - On macOS: brew services start mongodb-community"
    echo "   - On Ubuntu: sudo systemctl start mongod"
    echo "   - Or run: mongod"
fi

echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

echo "🗄️  Setting up database..."
cd backend
python3 sample_data.py
cd ..

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "1. Start MongoDB (if not already running)"
echo "2. Run: ./start.sh"
echo ""
echo "Or start manually:"
echo "Backend:  cd backend && python3 app.py"
echo "Frontend: cd frontend && npm run dev"
