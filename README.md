# CSE-AIML ERP System

A read-only ERP system for CSE-AIML class management with Flask backend and Next.js frontend.

## Features

- **Students Management**: View student records with roll numbers, contact info, and academic details
- **Faculty Management**: View faculty records with employee IDs, designations, and subject assignments
- **Course Management**: View course information including codes, credits, and descriptions
- **Leave Management**: View leave applications with dates and reasons
- **Dashboard**: Overview statistics and quick navigation

## Tech Stack

- **Backend**: Python Flask with MongoDB
- **Frontend**: Next.js (JavaScript)
- **Database**: MongoDB

## Setup Instructions

### Prerequisites

- Python 3.7+
- Node.js 16+
- MongoDB (local or cloud)

### Quick Setup (Recommended)

**For macOS/Linux:**
```bash
# Make setup script executable and run it
chmod +x setup.sh
./setup.sh

# Start the application
./start.sh
```

**For Windows:**
```cmd
# Run the setup script
setup.bat

# Start the application
start.bat
```

### Manual Setup

#### 1. Backend Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cd backend
   cp env.example .env
   # Edit .env file if needed
   ```

3. Start MongoDB:
   ```bash
   # On macOS with Homebrew:
   brew services start mongodb-community
   
   # On Ubuntu:
   sudo systemctl start mongod
   
   # Or run directly:
   mongod
   ```

4. Populate sample data:
   ```bash
   cd backend
   python sample_data.py
   ```

5. Start the Flask backend:
   ```bash
   cd backend
   python app.py
   ```
   The backend will run on `http://localhost:5000`

#### 2. Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will run on `http://localhost:3002`

## Database Schema

### Students Collection
```javascript
{
  "_id": ObjectId("..."),
  "roll": 12,
  "fullName": "Aisha Khan",
  "email": "aisha@college.edu",
  "phone": "+91-98XXXXXXX",
  "year": 4,
  "batch": 2024,
  "dateOfBirth": ISODate("2003-05-12"),
  "addresses": [
    {"type":"permanent","line1":"...","city":"...","state":"...","pincode":"..."}
  ]
}
```

### Faculties Collection
```javascript
{
  "_id": ObjectId("..."),
  "employeeId": "FAC-01",
  "fullName": "Dr. R. Sen",
  "email": "rsen@college.edu",
  "designation": "Associate Professor",
  "subjects": [ ObjectId("courseId1"), ObjectId("courseId2") ]
}
```

### Courses Collection
```javascript
{
  "_id": ObjectId("..."),
  "code": "CSE401",
  "title": "Machine Learning",
  "credits": 3,
  "facultyInCharge": ObjectId("..."),
  "semester": 7,
  "description": "Intro to ML"
}
```

### Leaves Collection
```javascript
{
  "_id": ObjectId("..."),
  "studentId": ObjectId("..."),
  "startDate": ISODate("2024-08-15"),
  "endDate": ISODate("2024-08-17"),
  "reason": "Medical - fever",
  "handledBy": ObjectId("facultyOrAdminId") // optional
}
```

## API Endpoints

- `GET /api/dashboard` - Dashboard statistics
- `GET /api/students` - Get all students
- `GET /api/students/<id>` - Get specific student
- `GET /api/faculties` - Get all faculties
- `GET /api/faculties/<id>` - Get specific faculty
- `GET /api/courses` - Get all courses
- `GET /api/courses/<id>` - Get specific course
- `GET /api/leaves` - Get all leaves
- `GET /api/leaves/<id>` - Get specific leave

## Usage

1. Start both backend and frontend servers
2. Open `http://localhost:3002` in your browser
3. Navigate through the different sections using the navigation bar
4. All data is read-only as designed for MCP integration

## Future MCP Integration

This ERP system is designed to be integrated with Model Context Protocol (MCP) for natural language data manipulation. The current read-only interface will be enhanced with MCP capabilities for:

- Adding new records
- Updating existing records
- Deleting records
- Complex queries and reports
- Natural language interactions

## Development Notes

- The system uses CORS to allow frontend-backend communication
- All ObjectIds are converted to strings for JSON serialization
- The interface is responsive and mobile-friendly
- Error handling is implemented for API failures
