#!/usr/bin/env python3
"""
Setup script for CSE-AIML ERP MCP Server.
This script handles the complete setup process including dependencies, environment, and sample data.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8 or higher is required")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def check_mongodb():
    """Check if MongoDB is available."""
    try:
        result = subprocess.run("mongod --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ MongoDB is installed")
            return True
        else:
            print("✗ MongoDB is not installed or not in PATH")
            print("Please install MongoDB from https://www.mongodb.com/try/download/community")
            return False
    except:
        print("✗ MongoDB is not installed or not in PATH")
        print("Please install MongoDB from https://www.mongodb.com/try/download/community")
        return False


def create_virtual_environment():
    """Create virtual environment."""
    if not os.path.exists("venv"):
        return run_command("python -m venv venv", "Creating virtual environment")
    else:
        print("✓ Virtual environment already exists")
        return True


def activate_and_install():
    """Activate virtual environment and install dependencies."""
    # Determine activation script based on OS
    if os.name == 'nt':  # Windows
        activate_script = "venv\\Scripts\\activate"
        python_executable = "venv\\Scripts\\python"
        pip_executable = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        activate_script = "source venv/bin/activate"
        python_executable = "venv/bin/python"
        pip_executable = "venv/bin/pip"
    
    # Install dependencies
    if not run_command(f"{pip_executable} install --upgrade pip", "Upgrading pip"):
        return False
    
    if not run_command(f"{pip_executable} install -r requirements.txt", "Installing dependencies"):
        return False
    
    return True


def setup_environment():
    """Set up environment configuration."""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("✓ Created .env file from env.example")
            print("⚠️  Please edit .env file with your MongoDB connection details")
        else:
            # Create basic .env file
            with open(env_file, 'w') as f:
                f.write("MONGO_URI=mongodb://localhost:27017/\n")
                f.write("DATABASE_NAME=cse_aiml_erp\n")
                f.write("MCP_SERVER_NAME=cse-aiml-erp-server\n")
            print("✓ Created basic .env file")
            print("⚠️  Please edit .env file with your MongoDB connection details")
    else:
        print("✓ .env file already exists")


def create_startup_scripts():
    """Create startup scripts for different platforms."""
    
    # Windows batch script
    with open("start_server.bat", "w") as f:
        f.write("""@echo off
echo Starting CSE-AIML ERP MCP Server...
call venv\\Scripts\\activate
python src\\main.py
pause
""")
    
    # Unix shell script
    with open("start_server.sh", "w") as f:
        f.write("""#!/bin/bash
echo "Starting CSE-AIML ERP MCP Server..."
source venv/bin/activate
python src/main.py
""")
    
    # Make shell script executable
    if os.name != 'nt':
        os.chmod("start_server.sh", 0o755)
    
    print("✓ Created startup scripts (start_server.bat for Windows, start_server.sh for Unix)")


def setup_mongodb():
    """Provide MongoDB setup instructions."""
    print("\n" + "="*60)
    print("MONGODB SETUP INSTRUCTIONS")
    print("="*60)
    print("1. Install MongoDB Community Edition:")
    print("   - Windows: Download from https://www.mongodb.com/try/download/community")
    print("   - macOS: brew install mongodb-community")
    print("   - Ubuntu: sudo apt-get install mongodb")
    print("")
    print("2. Start MongoDB service:")
    print("   - Windows: net start MongoDB")
    print("   - macOS: brew services start mongodb-community")
    print("   - Ubuntu: sudo systemctl start mongod")
    print("")
    print("3. Verify MongoDB is running:")
    print("   - Run: mongod --version")
    print("   - Connect: mongosh")
    print("")
    print("4. The server will automatically create the database and collections")
    print("="*60)


def create_sample_data_script():
    """Create a script to populate sample data."""
    sample_script = """#!/usr/bin/env python3
\"\"\"
Quick sample data creation script.
\"\"\"

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sample_data import create_sample_data

async def main():
    await create_sample_data()

if __name__ == "__main__":
    asyncio.run(main())
"""
    
    with open("create_sample_data.py", "w") as f:
        f.write(sample_script)
    
    if os.name != 'nt':
        os.chmod("create_sample_data.py", 0o755)
    
    print("✓ Created create_sample_data.py script")


def main():
    """Main setup function."""
    print("CSE-AIML ERP MCP Server Setup")
    print("="*40)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_mongodb():
        setup_mongodb()
        response = input("Continue setup without MongoDB? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Setup steps
    steps = [
        ("Creating virtual environment", create_virtual_environment),
        ("Installing dependencies", activate_and_install),
        ("Setting up environment", setup_environment),
        ("Creating startup scripts", create_startup_scripts),
        ("Creating sample data script", create_sample_data_script),
    ]
    
    for description, func in steps:
        print(f"\n{description}...")
        if not func():
            print(f"Setup failed at: {description}")
            sys.exit(1)
    
    print("\n" + "="*60)
    print("SETUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("Next steps:")
    print("1. Edit .env file with your MongoDB connection details")
    print("2. Start MongoDB service")
    print("3. Run: python create_sample_data.py (optional - for sample data)")
    print("4. Start the server:")
    print("   - Windows: start_server.bat")
    print("   - Unix: ./start_server.sh")
    print("   - Or manually: python src/main.py")
    print("")
    print("For Claude Desktop integration, add to your configuration:")
    print('{"mcpServers": {"cse-aiml-erp": {"command": "python", "args": ["/path/to/mcp_server/src/main.py"]}}}')
    print("="*60)


if __name__ == "__main__":
    main()
