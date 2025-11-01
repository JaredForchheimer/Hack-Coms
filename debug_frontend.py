#!/usr/bin/env python3
"""
Frontend Debug Script

This script helps debug frontend issues by checking common problems.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_banner():
    """Print debug banner."""
    print("=" * 60)
    print("🔍 FRONTEND DEBUG SCRIPT")
    print("=" * 60)
    print()

def check_file_exists(file_path, description):
    """Check if a file exists and print result."""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description} MISSING: {file_path}")
        return False

def check_package_json():
    """Check package.json for issues."""
    print("📦 Checking package.json...")
    
    package_file = Path("asl-summarizer-frontend/package.json")
    if not package_file.exists():
        print("❌ package.json not found")
        return False
    
    try:
        with open(package_file, 'r') as f:
            package_data = json.load(f)
        
        print(f"✅ Package name: {package_data.get('name', 'unknown')}")
        print(f"✅ Package version: {package_data.get('version', 'unknown')}")
        
        # Check dependencies
        deps = package_data.get('dependencies', {})
        required_deps = ['react', 'react-dom', 'react-router-dom']
        
        for dep in required_deps:
            if dep in deps:
                print(f"✅ {dep}: {deps[dep]}")
            else:
                print(f"❌ Missing dependency: {dep}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading package.json: {e}")
        return False

def check_vite_config():
    """Check Vite configuration."""
    print("\n⚙️ Checking Vite config...")
    
    vite_file = Path("asl-summarizer-frontend/vite.config.js")
    if not vite_file.exists():
        print("❌ vite.config.js not found")
        return False
    
    try:
        with open(vite_file, 'r') as f:
            content = f.read()
        
        if 'port: 5173' in content:
            print("✅ Vite configured for port 5173")
        else:
            print("⚠️ Vite port may not be 5173")
        
        print("✅ Vite config exists")
        return True
        
    except Exception as e:
        print(f"❌ Error reading vite.config.js: {e}")
        return False

def check_main_files():
    """Check main React files."""
    print("\n📁 Checking main React files...")
    
    files_to_check = [
        ("asl-summarizer-frontend/index.html", "HTML entry point"),
        ("asl-summarizer-frontend/src/main.jsx", "React entry point"),
        ("asl-summarizer-frontend/src/App.jsx", "Main App component"),
        ("asl-summarizer-frontend/src/styles/globals.css", "Global styles"),
        ("asl-summarizer-frontend/src/context/AuthContext.jsx", "Auth context"),
        ("asl-summarizer-frontend/src/pages/HomePage/HomePage.jsx", "Home page"),
        ("asl-summarizer-frontend/src/components/auth/ProtectedRoute/ProtectedRoute.jsx", "Protected route")
    ]
    
    all_exist = True
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def check_node_modules():
    """Check if node_modules exists."""
    print("\n📦 Checking node_modules...")
    
    node_modules = Path("asl-summarizer-frontend/node_modules")
    if node_modules.exists():
        print("✅ node_modules directory exists")
        
        # Check for key packages
        key_packages = ['react', 'react-dom', 'vite']
        for package in key_packages:
            package_dir = node_modules / package
            if package_dir.exists():
                print(f"✅ {package} installed")
            else:
                print(f"❌ {package} not found in node_modules")
        
        return True
    else:
        print("❌ node_modules directory not found")
        print("   Run: cd asl-summarizer-frontend && npm install")
        return False

def test_build():
    """Test if the project can build."""
    print("\n🔨 Testing build...")
    
    frontend_dir = Path("asl-summarizer-frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    try:
        # Try to run npm run build
        result = subprocess.run([
            "npm", "run", "build"
        ], cwd=frontend_dir, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Build successful")
            return True
        else:
            print("❌ Build failed")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️ Build timed out")
        return False
    except Exception as e:
        print(f"❌ Build test failed: {e}")
        return False

def check_browser_console_instructions():
    """Provide instructions for checking browser console."""
    print("\n🌐 Browser Console Debug Instructions:")
    print("=" * 40)
    print("1. Open your browser and go to http://localhost:5173")
    print("2. Press F12 to open Developer Tools")
    print("3. Go to the Console tab")
    print("4. Look for any error messages (red text)")
    print("5. Check the Network tab for failed requests")
    print()
    print("Common errors to look for:")
    print("- 'Failed to fetch' - Backend not running")
    print("- 'Module not found' - Missing dependencies")
    print("- 'Syntax error' - Code compilation issues")
    print("- 'CORS error' - Backend CORS misconfiguration")
    print()

def provide_solutions():
    """Provide common solutions."""
    print("🔧 Common Solutions:")
    print("=" * 40)
    print()
    print("1. If node_modules is missing:")
    print("   cd asl-summarizer-frontend")
    print("   npm install")
    print()
    print("2. If build fails:")
    print("   cd asl-summarizer-frontend")
    print("   rm -rf node_modules package-lock.json")
    print("   npm install")
    print()
    print("3. If port issues:")
    print("   Check if port 5173 is already in use")
    print("   Kill any existing processes on port 5173")
    print()
    print("4. If still blank page:")
    print("   Check browser console for JavaScript errors")
    print("   Verify backend is running on port 5000")
    print("   Check network requests in browser dev tools")
    print()

def main():
    """Main debug function."""
    print_banner()
    
    # Check all components
    package_ok = check_package_json()
    vite_ok = check_vite_config()
    files_ok = check_main_files()
    modules_ok = check_node_modules()
    
    print("\n" + "=" * 60)
    print("📊 DEBUG SUMMARY")
    print("=" * 60)
    
    if package_ok and vite_ok and files_ok and modules_ok:
        print("✅ All basic checks passed!")
        print("🔨 Testing build process...")
        
        build_ok = test_build()
        
        if build_ok:
            print("\n🎉 Frontend appears to be set up correctly!")
            print("If you're still seeing a blank page:")
            check_browser_console_instructions()
        else:
            print("\n❌ Build failed - this is likely the issue")
            provide_solutions()
    else:
        print("❌ Some checks failed - these need to be fixed first")
        provide_solutions()
    
    print("\n" + "=" * 60)
    print("Next steps:")
    print("1. Fix any issues shown above")
    print("2. Start the frontend: cd asl-summarizer-frontend && npm run dev")
    print("3. Check browser console at http://localhost:5173")
    print("4. Verify backend is running at http://localhost:5000")
    print("=" * 60)

if __name__ == "__main__":
    main()