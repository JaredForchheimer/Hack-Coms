#!/usr/bin/env python3
"""
ASL Summarizer Application Fix Script

This script fixes all identified issues with the ASL Summarizer application.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print fix banner."""
    print("=" * 60)
    print("🔧 ASL SUMMARIZER - APPLICATION FIX SCRIPT")
    print("=" * 60)
    print()

def fix_backend_dependencies():
    """Fix backend dependencies, especially the Anthropic library."""
    print("🐍 Fixing backend dependencies...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    try:
        # Upgrade pip first
        print("📦 Upgrading pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Install/upgrade the Anthropic library specifically
        print("🤖 Upgrading Anthropic library...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "anthropic>=0.25.0"], 
                      check=True, capture_output=True)
        
        # Install all backend requirements
        print("📋 Installing backend requirements...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Backend dependencies fixed")
            return True
        else:
            print(f"❌ Failed to install backend dependencies: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing backend dependencies: {e}")
        return False

def fix_frontend_dependencies():
    """Fix frontend dependencies and configuration."""
    print("\n📦 Fixing frontend dependencies...")
    
    frontend_dir = Path("asl-summarizer-frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    try:
        # Remove node_modules and package-lock.json for clean install
        node_modules = frontend_dir / "node_modules"
        package_lock = frontend_dir / "package-lock.json"
        
        if node_modules.exists():
            print("🗑️ Removing old node_modules...")
            import shutil
            shutil.rmtree(node_modules)
        
        if package_lock.exists():
            print("🗑️ Removing package-lock.json...")
            package_lock.unlink()
        
        # Fresh npm install
        print("📦 Fresh npm install...")
        result = subprocess.run([
            "npm", "install"
        ], cwd=frontend_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Frontend dependencies fixed")
            return True
        else:
            print(f"❌ Failed to install frontend dependencies: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing frontend dependencies: {e}")
        return False

def test_anthropic_import():
    """Test if the Anthropic library can be imported correctly."""
    print("\n🧪 Testing Anthropic library...")
    
    try:
        # Test import
        result = subprocess.run([
            sys.executable, "-c", 
            "from anthropic import Anthropic; client = Anthropic(api_key='test'); print('✅ Anthropic import successful')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Anthropic library working correctly")
            return True
        else:
            print(f"❌ Anthropic library test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Anthropic library: {e}")
        return False

def check_environment_file():
    """Check and fix environment file."""
    print("\n⚙️ Checking environment configuration...")
    
    env_file = Path("backend/.env")
    if not env_file.exists():
        print("⚠️ Creating .env file from example...")
        example_file = Path("backend/.env.example")
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print("✅ Created .env file")
        else:
            print("❌ .env.example not found")
            return False
    
    # Check for API key
    try:
        with open(env_file, 'r') as f:
            content = f.read()
        
        if "ANTHROPIC_API_KEY=sk-" not in content:
            print("⚠️ ANTHROPIC_API_KEY not properly set in .env")
            print("   Please add your API key to backend/.env")
            return False
        else:
            print("✅ Environment configuration looks good")
            return True
            
    except Exception as e:
        print(f"❌ Error checking environment file: {e}")
        return False

def test_backend_startup():
    """Test if backend can start without errors."""
    print("\n🚀 Testing backend startup...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    try:
        # Try to import the main modules
        test_script = """
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

try:
    from app import create_app
    from app.services.claude_service import ClaudeService
    print('✅ Backend modules import successfully')
except Exception as e:
    print(f'❌ Backend import error: {e}')
    sys.exit(1)
"""
        
        result = subprocess.run([
            sys.executable, "-c", test_script
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            print("✅ Backend startup test passed")
            return True
        else:
            print(f"❌ Backend startup test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing backend startup: {e}")
        return False

def test_frontend_build():
    """Test if frontend can build successfully."""
    print("\n🔨 Testing frontend build...")
    
    frontend_dir = Path("asl-summarizer-frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    try:
        result = subprocess.run([
            "npm", "run", "build"
        ], cwd=frontend_dir, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ Frontend build test passed")
            return True
        else:
            print(f"❌ Frontend build test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️ Frontend build test timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing frontend build: {e}")
        return False

def provide_final_instructions():
    """Provide final instructions to the user."""
    print("\n" + "=" * 60)
    print("📋 FINAL INSTRUCTIONS")
    print("=" * 60)
    print()
    print("1. Start the backend:")
    print("   cd backend")
    print("   python run.py")
    print()
    print("2. In a new terminal, start the frontend:")
    print("   cd asl-summarizer-frontend")
    print("   npm run dev")
    print()
    print("3. Open your browser to:")
    print("   http://localhost:5173")
    print()
    print("4. If you still see a blank page:")
    print("   - Press F12 to open Developer Tools")
    print("   - Check the Console tab for JavaScript errors")
    print("   - Check the Network tab for failed requests")
    print()
    print("5. Verify backend is working:")
    print("   http://localhost:5000/health/")
    print()
    print("=" * 60)

def main():
    """Main fix function."""
    print_banner()
    
    success_count = 0
    total_tests = 6
    
    # Fix dependencies
    if fix_backend_dependencies():
        success_count += 1
    
    if fix_frontend_dependencies():
        success_count += 1
    
    # Test components
    if test_anthropic_import():
        success_count += 1
    
    if check_environment_file():
        success_count += 1
    
    if test_backend_startup():
        success_count += 1
    
    if test_frontend_build():
        success_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FIX SUMMARY")
    print("=" * 60)
    print(f"✅ Successful fixes: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 All fixes applied successfully!")
        print("Your application should now work correctly.")
    elif success_count >= 4:
        print("⚠️ Most fixes applied successfully.")
        print("There may be minor issues remaining.")
    else:
        print("❌ Several issues remain.")
        print("Please check the error messages above.")
    
    provide_final_instructions()
    
    return 0 if success_count >= 4 else 1

if __name__ == "__main__":
    sys.exit(main())