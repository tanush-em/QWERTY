# CSE-AIML ERP MCP Server

A Model Context Protocol (MCP) server for the CSE-AIML ERP system that provides tools for managing students, faculty, courses, leaves, timetables, analytics, and reports.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   - Copy `env.example` to `.env`
   - Update MongoDB connection details in `.env`

3. **Start MongoDB:**
   ```bash
   # macOS
   brew services start mongodb-community
   
   # Linux
   sudo systemctl start mongod
   
   # Windows
   net start MongoDB
   ```

4. **Run the server:**
   ```bash
   python start_server.py
   ```

## Claude Desktop Integration

Add this to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "cse-aiml-erp": {
      "command": "/path/to/mcp_server/env/bin/python",
      "args": ["/path/to/mcp_server/start_server.py"]
    }
  }
}
```

**Important:** Use the virtual environment Python (`env/bin/python`) instead of the system Python to ensure all dependencies are available.

## Available Tools

The server provides 57+ tools across these categories:
- **Students**: CRUD operations, search, filtering
- **Faculty**: Management, workload tracking, subject assignment
- **Courses**: Course management, faculty assignment, statistics
- **Leaves**: Leave applications, approval workflow, analytics
- **Timetable**: Schedule management, room availability, faculty schedules
- **Analytics**: Enrollment stats, attendance, demographic analysis
- **Reports**: Data export, summary dashboards, formatted reports

## Database Structure

The server uses MongoDB with the following collections:
- `students` - Student records
- `faculties` - Faculty records  
- `courses` - Course information
- `leaves` - Leave applications
- `timetables` - Schedule data

## Environment Variables

- `MONGO_URI`: MongoDB connection string (default: mongodb://localhost:27017/)
- `DATABASE_NAME`: Database name (default: cse_aiml_erp)
- `MCP_SERVER_NAME`: Server name for MCP (default: cse-aiml-erp-server)