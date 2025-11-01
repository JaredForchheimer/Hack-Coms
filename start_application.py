#!/usr/bin/env python3
"""
ASL Summarizer Application Startup Script

This script helps you start the ASL Summarizer application with proper setup.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def print_banner():
    """Print application banner."""
    print("=" * 60)
    print("🤟 ASL SUMMARIZER - APPLICATION STARTUP")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_node_version():
    """Check if Node.js is installed."""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js version: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Error: Node.js is not installed or not in PATH")
    print("   Please install Node.js 16+ from https://nodejs.org/")
    return False

def check_postgresql():
    """Check if PostgreSQL is running."""
    try:
        # Try to connect to PostgreSQL
        result = subprocess.run(['pg_isready'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PostgreSQL is running")
            return True
    except FileNotFoundError:
        pass
    
    print("⚠️  Warning: PostgreSQL may not be running or pg_isready not found")
    print("   Please ensure PostgreSQL is installed and running")
    return False

def setup_database():
    """Initialize database if needed."""
    print("\n📊 Setting up database...")
    
    # Check if database handler exists
    if not Path("database_handler").exists():
        print("❌ Error: database_handler directory not found")
        return False
    
    try:
        # Try to initialize database
        result = subprocess.run([
            sys.executable, 
            "database_handler/scripts/init_db.py", 
            "--check"
        ], capture_output=True, text=True)
        
        if "Connection successful: True" in result.stdout:
            print("✅ Database connection successful")
            return True
        else:
            print("🔧 Initializing database...")
            init_result = subprocess.run([
                sys.executable, 
                "database_handler/scripts/init_db.py"
            ], capture_output=True, text=True)
            
            if init_result.returncode == 0:
                print("✅ Database initialized successfully")
                return True
            else:
                print(f"❌ Database initialization failed: {init_result.stderr}")
                return False
                
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False

def install_backend_dependencies():
    """Install backend Python dependencies."""
    print("\n🐍 Installing backend dependencies...")
    
    if not Path("backend/requirements.txt").exists():
        print("❌ Error: backend/requirements.txt not found")
        return False
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Backend dependencies installed")
            return True
        else:
            print(f"❌ Failed to install backend dependencies: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Backend dependency installation error: {e}")
        return False

def install_frontend_dependencies():
    """Install frontend Node.js dependencies."""
    print("\n📦 Installing frontend dependencies...")
    
    frontend_dir = Path("asl-summarizer-frontend")
    if not frontend_dir.exists():
        print("❌ Error: asl-summarizer-frontend directory not found")
        return False
    
    if not (frontend_dir / "package.json").exists():
        print("❌ Error: package.json not found in frontend directory")
        return False
    
    try:
        result = subprocess.run([
            "npm", "install"
        ], cwd=frontend_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Frontend dependencies installed")
            return True
        else:
            print(f"❌ Failed to install frontend dependencies: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend dependency installation error: {e}")
        return False

def check_env_file():
    """Check if backend .env file exists and has required variables."""
    print("\n⚙️  Checking configuration...")
    
    env_file = Path("backend/.env")
    if not env_file.exists():
        print("⚠️  Warning: backend/.env file not found")
        print("   Creating from example...")
        
        example_file = Path("backend/.env.example")
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print("✅ Created .env file from example")
            print("   Please edit backend/.env and add your ANTHROPIC_API_KEY")
        else:
            print("❌ Error: .env.example file not found")
            return False
    
    # Check for required variables
    try:
        with open(env_file, 'r') as f:
            content = f.read()
            
        required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        missing_vars = []
        
        for var in required_vars:
            if f"{var}=" not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️  Warning: Missing required variables in .env: {', '.join(missing_vars)}")
        else:
            print("✅ Configuration file looks good")
        
        if "ANTHROPIC_API_KEY=" not in content or "ANTHROPIC_API_KEY=sk-" not in content:
            print("⚠️  Warning: ANTHROPIC_API_KEY not set in .env file")
            print("   Some features may not work without a valid API key")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def start_backend():
    """Start the backend server."""
    print("\n🚀 Starting backend server...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Error: backend directory not found")
        return None
    
    try:
        # Start backend server
        process = subprocess.Popen([
            sys.executable, "run.py"
        ], cwd=backend_dir)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:5000/health/", timeout=5)
            if response.status_code == 200:
                print("✅ Backend server started successfully")
                print("   URL: http://localhost:5000")
                return process
            else:
                print(f"⚠️  Backend server started but health check failed: {response.status_code}")
                return process
        except requests.exceptions.RequestException:
            print("⚠️  Backend server started but health check failed")
            return process
            
    except Exception as e:
        print(f"❌ Failed to start backend server: {e}")
        return None

def start_frontend():
    """Start the frontend development server."""
    print("\n🎨 Starting frontend server...")
    
    frontend_dir = Path("asl-summarizer-frontend")
    if not frontend_dir.exists():
        print("❌ Error: asl-summarizer-frontend directory not found")
        return None
    
    try:
        # Start frontend server
        process = subprocess.Popen([
            "npm", "run", "dev"
        ], cwd=frontend_dir)
        
        # Wait a moment for server to start
        time.sleep(5)
        
        print("✅ Frontend server started")
        print("   URL: http://localhost:5173")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start frontend server: {e}")
        return None

def main():
    """Main startup function."""
    print_banner()
    
    # Check prerequisites
    if not check_python_version():
        return 1
    
    if not check_node_version():
        return 1
    
    check_postgresql()
    
    # Setup and install dependencies
    if not check_env_file():
        return 1
    
    if not install_backend_dependencies():
        return 1
    
    if not install_frontend_dependencies():
        return 1
    
    if not setup_database():
        print("⚠️  Database setup failed, but continuing...")
    
    # Start servers
    backend_process = start_backend()
    if not backend_process:
        return 1
    
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        return 1
    
    # Success message
    print("\n" + "=" * 60)
    print("🎉 ASL SUMMARIZER STARTED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("📱 Frontend: http://localhost:5173")
    print("🔧 Backend:  http://localhost:5000")
    print("💊 Health:   http://localhost:5000/health/")
    print()
    print("Press Ctrl+C to stop both servers")
    print("=" * 60)
    
    try:
        # Wait for user to stop
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping servers...")
        frontend_process.terminate()
        backend_process.terminate()
        print("✅ Servers stopped")
        return 0

if __name__ == "__main__":
    sys.exit(main())