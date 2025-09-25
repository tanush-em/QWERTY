#!/usr/bin/env python3
"""
Test script to verify the ERP system setup
"""

import sys
import os
import subprocess
import time

def test_python_dependencies():
    """Test if Python dependencies are installed"""
    print("🔍 Testing Python dependencies...")
    try:
        import flask
        import pymongo
        from flask_cors import CORS
        from dotenv import load_dotenv
        print("✅ Python dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        return False

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("🔍 Testing MongoDB connection...")
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/')
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB is running and accessible")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("   Please start MongoDB: mongod")
        return False

def test_backend_startup():
    """Test if backend can start"""
    print("🔍 Testing backend startup...")
    try:
        # Change to backend directory
        os.chdir('backend')
        
        # Import the app
        sys.path.append('.')
        from app import app
        
        # Test if app can be created
        with app.test_client() as client:
            print("✅ Backend app can be created")
            return True
    except Exception as e:
        print(f"❌ Backend startup failed: {e}")
        return False
    finally:
        # Change back to root directory
        os.chdir('..')

def test_node_dependencies():
    """Test if Node.js dependencies are installed"""
    print("🔍 Testing Node.js dependencies...")
    try:
        result = subprocess.run(['npm', 'list', '--depth=0'], 
                              cwd='frontend', 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        if result.returncode == 0:
            print("✅ Node.js dependencies are installed")
            return True
        else:
            print("❌ Node.js dependencies not properly installed")
            return False
    except Exception as e:
        print(f"❌ Node.js test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing CSE-AIML ERP System Setup")
    print("=" * 50)
    
    tests = [
        test_python_dependencies,
        test_mongodb_connection,
        test_backend_startup,
        test_node_dependencies
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your ERP system is ready to run.")
        print("\nTo start the application:")
        print("  ./start.sh  (macOS/Linux)")
        print("  start.bat   (Windows)")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Install Node.js dependencies: cd frontend && npm install")
        print("  3. Start MongoDB: mongod")
        print("  4. Run setup script: ./setup.sh")

if __name__ == "__main__":
    main()
