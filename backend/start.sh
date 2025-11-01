#!/bin/bash

# ASL Summarizer Backend Startup Script

echo "🚀 Starting ASL Summarizer Backend Server..."
echo "================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

# Check if PostgreSQL is running (optional check)
if command -v pg_isready &> /dev/null; then
    if ! pg_isready -q; then
        echo "⚠️  Warning: PostgreSQL may not be running"
    else
        echo "✅ PostgreSQL is running"
    fi
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Creating from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file from template"
        echo "⚠️  Please edit .env file with your configuration before continuing"
        echo "   Required: ANTHROPIC_API_KEY, database credentials"
        exit 1
    else
        echo "❌ .env.example file not found"
        exit 1
    fi
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📋 Installing Python dependencies..."
pip install -r requirements.txt

# Check critical environment variables
source .env
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ANTHROPIC_API_KEY not set in .env file"
    exit 1
fi

if [ -z "$DB_PASSWORD" ]; then
    echo "❌ DB_PASSWORD not set in .env file"
    exit 1
fi

echo "✅ Environment variables configured"

# Initialize database if needed
echo "🗄️  Checking database..."
cd ..
if [ -f "database_handler/scripts/init_db.py" ]; then
    echo "🔄 Initializing database (if needed)..."
    python database_handler/scripts/init_db.py --check || {
        echo "🏗️  Setting up database..."
        python database_handler/scripts/init_db.py
    }
    echo "✅ Database ready"
else
    echo "⚠️  Database initialization script not found"
fi
cd backend

# Start the server
echo "🌟 Starting Flask server..."
echo "📍 Server will be available at: http://localhost:${FLASK_PORT:-5000}"
echo "🔍 Health check: http://localhost:${FLASK_PORT:-5000}/health/"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================================"

python run.py