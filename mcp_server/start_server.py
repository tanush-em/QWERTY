#!/usr/bin/env python3
"""
Simple startup script for the MCP server.
"""
import asyncio
import sys
import os

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(script_dir, 'src')

# Add src directory to Python path
sys.path.insert(0, src_path)

# Change to src directory to ensure imports work
os.chdir(src_path)

try:
    from main import main
    
    if __name__ == "__main__":
        asyncio.run(main())
        
except ImportError as e:
    # Don't print to stdout - this breaks MCP protocol
    import sys
    sys.stderr.write(f"Import error: {e}\n")
    sys.stderr.write("Make sure you're running this from the mcp_server directory\n")
    sys.exit(1)
except Exception as e:
    # Don't print to stdout - this breaks MCP protocol
    import sys
    sys.stderr.write(f"Error starting server: {e}\n")
    sys.exit(1)
