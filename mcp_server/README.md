# CSE-AIML ERP MCP Server

A comprehensive Model Context Protocol (MCP) server for managing a CSE-AIML ERP system. This server provides full CRUD operations, complex aggregation queries, and report generation capabilities through direct MongoDB connection.

## Features

### Core Management Modules
- **Student Management**: Complete CRUD operations for student records
- **Faculty Management**: Faculty member management with workload tracking
- **Course Management**: Course catalog management with faculty assignments
- **Leave Management**: Leave application system with approval workflow
- **Timetable Management**: Class scheduling and room management

### Advanced Features
- **Analytics & Reporting**: Comprehensive data analysis and reporting
- **Search & Filtering**: Advanced search capabilities across all modules
- **Data Export**: CSV and JSON export functionality
- **Real-time Statistics**: Live dashboard with key metrics
- **Conflict Detection**: Room and schedule conflict detection

## Installation

### Prerequisites
- Python 3.8 or higher
- MongoDB 4.4 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or Download the Project**
   ```bash
   cd /path/to/your/project
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp env.example .env
   # Edit .env with your MongoDB connection details
   ```

5. **Set Up MongoDB**
   - Install and start MongoDB
   - Create a database named `cse_aiml_erp` (or update .env)
   - The server will create collections automatically

6. **Configure Claude Desktop (Optional)**
   Add to your Claude Desktop configuration:
   ```json
   {
     "mcpServers": {
       "cse-aiml-erp": {
         "command": "python",
         "args": ["/path/to/mcp_server/src/main.py"],
         "env": {
           "MONGO_URI": "mongodb://localhost:27017/",
           "DATABASE_NAME": "cse_aiml_erp"
         }
       }
     }
   }
   ```

## Usage

### Starting the Server

```bash
python src/main.py
```

The server will start and listen for MCP connections. You can interact with it through Claude Desktop or any MCP-compatible client.

### Basic Operations

#### Student Management
```python
# Get all students
await get_students(page=1, page_size=50)

# Create a new student
await create_student(
    roll="CSE001",
    full_name="John Doe",
    email="john.doe@example.com",
    year="2024",
    batch="A"
)

# Search students
await search_students(query="John", search_fields=["fullName", "email"])
```

#### Faculty Management
```python
# Get faculty members
await get_faculties(designation="Professor")

# Assign subjects to faculty
await assign_subjects_to_faculty(
    faculty_id="faculty_id_here",
    subjects=["Data Structures", "Algorithms"]
)

# Get faculty workload
await get_faculty_workload("faculty_id_here")
```

#### Course Management
```python
# Create a course
await create_course(
    code="CS101",
    title="Introduction to Programming",
    credits=3,
    semester=1
)

# Assign faculty to course
await assign_faculty_to_course("course_id", "faculty_id")
```

#### Leave Management
```python
# Create leave application
await create_leave(
    student_id="student_id",
    start_date="2024-01-15",
    end_date="2024-01-17",
    reason="Medical emergency"
)

# Approve leave
await approve_leave(
    leave_id="leave_id",
    handled_by="faculty_id",
    remarks="Approved"
)
```

#### Timetable Management
```python
# Create timetable slot
await create_timetable_slot(
    day_of_week="monday",
    period=1,
    start_time="09:00",
    end_time="10:00",
    slot_type="class",
    course_code="CS101",
    faculty_id="faculty_id",
    room="A101"
)

# Check room availability
await check_room_availability(
    room="A101",
    day_of_week="monday",
    start_time="09:00",
    end_time="10:00"
)
```

### Analytics and Reporting

```python
# Get enrollment statistics
await get_enrollment_stats()

# Generate academic report
await generate_academic_report()

# Export data to CSV
await export_data_csv("students", {"year": "2024"})

# Generate student list
await generate_student_list(year="2024", format_type="csv")
```

## Database Schema

### Students Collection
```json
{
  "_id": "ObjectId",
  "roll": "CSE001",
  "fullName": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "year": "2024",
  "batch": "A",
  "dateOfBirth": "2000-01-01",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

### Faculties Collection
```json
{
  "_id": "ObjectId",
  "employeeId": "EMP001",
  "fullName": "Dr. Jane Smith",
  "email": "jane.smith@example.com",
  "phone": "+1234567890",
  "designation": "Professor",
  "subjects": ["Data Structures", "Algorithms"],
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

### Courses Collection
```json
{
  "_id": "ObjectId",
  "code": "CS101",
  "title": "Introduction to Programming",
  "credits": 3,
  "semester": 1,
  "facultyInCharge": "ObjectId",
  "description": "Basic programming concepts",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

### Leaves Collection
```json
{
  "_id": "ObjectId",
  "studentId": "ObjectId",
  "startDate": "2024-01-15",
  "endDate": "2024-01-17",
  "reason": "Medical emergency",
  "status": "approved",
  "handledBy": "ObjectId",
  "remarks": "Approved",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

### Timetables Collection
```json
{
  "_id": "ObjectId",
  "dayOfWeek": "monday",
  "slots": [
    {
      "period": 1,
      "startTime": "09:00",
      "endTime": "10:00",
      "type": "class",
      "courseCode": "CS101",
      "facultyId": "ObjectId",
      "room": "A101"
    }
  ],
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

## Available Tools

### Student Tools
- `get_students` - List students with filtering and pagination
- `get_student_by_id` - Get specific student details
- `create_student` - Add new student record
- `update_student` - Update existing student
- `delete_student` - Remove student record
- `search_students` - Search students by multiple criteria
- `get_students_by_year` - Filter students by academic year
- `get_students_by_batch` - Filter students by batch

### Faculty Tools
- `get_faculties` - List faculty members
- `get_faculty_by_id` - Get specific faculty details
- `create_faculty` - Add new faculty record
- `update_faculty` - Update existing faculty
- `delete_faculty` - Remove faculty record
- `search_faculties` - Search faculty members
- `assign_subjects_to_faculty` - Manage subject assignments
- `get_faculty_workload` - Calculate teaching load

### Course Tools
- `get_courses` - List all courses
- `get_course_by_id` - Get specific course details
- `create_course` - Add new course
- `update_course` - Update existing course
- `delete_course` - Remove course
- `search_courses` - Search courses
- `assign_faculty_to_course` - Assign faculty to course
- `get_courses_by_semester` - Filter courses by semester
- `get_course_statistics` - Get course analytics

### Leave Tools
- `get_leaves` - List leave applications
- `get_leave_by_id` - Get specific leave details
- `create_leave` - Submit leave application
- `update_leave` - Update leave application
- `delete_leave` - Cancel leave application
- `approve_leave` - Approve leave application
- `reject_leave` - Reject leave application
- `get_leaves_by_student` - Get student's leaves
- `get_pending_leaves` - Get pending applications
- `get_leave_statistics` - Get leave analytics

### Timetable Tools
- `get_timetable` - Get complete timetable
- `get_timetable_by_day` - Get day-specific schedule
- `create_timetable_slot` - Add new time slot
- `update_timetable_slot` - Update existing slot
- `delete_timetable_slot` - Remove time slot
- `get_faculty_schedule` - Get faculty-specific timetable
- `check_room_availability` - Check room conflicts
- `get_free_periods` - Find available time slots

### Analytics Tools
- `get_enrollment_stats` - Student enrollment analytics
- `get_attendance_summary` - Attendance statistics
- `get_leave_analytics` - Leave pattern analysis
- `get_faculty_workload_report` - Teaching load distribution
- `get_course_popularity` - Course enrollment trends
- `get_demographic_analysis` - Student demographics
- `generate_academic_report` - Comprehensive academic report

### Report Tools
- `generate_student_list` - Formatted student roster
- `generate_faculty_directory` - Faculty contact information
- `generate_course_catalog` - Complete course listing
- `generate_leave_report` - Leave status report
- `generate_timetable_report` - Formatted timetable
- `export_data_csv` - Export collections to CSV
- `generate_summary_dashboard` - Dashboard data compilation

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
MONGO_URI=mongodb://localhost:27017/
DATABASE_NAME=cse_aiml_erp
MCP_SERVER_NAME=cse-aiml-erp-server
MAX_CONNECTION_POOL_SIZE=10
CONNECTION_TIMEOUT=5000
SERVER_TIMEOUT=30000
DEFAULT_PAGE_SIZE=50
MAX_PAGE_SIZE=1000
LOG_LEVEL=INFO
```

### MongoDB Configuration

The server expects the following MongoDB setup:
- Database: `cse_aiml_erp` (configurable)
- Collections: Created automatically
- Indexes: Created automatically for better performance

## Error Handling

The server includes comprehensive error handling:
- Input validation for all operations
- Database connection error handling
- Graceful error responses with meaningful messages
- Logging for debugging and monitoring

## Performance Considerations

- Connection pooling for MongoDB
- Pagination for large datasets
- Efficient aggregation pipelines
- Indexed queries for better performance
- Async/await pattern for non-blocking operations

## Security

- Input validation and sanitization
- ObjectId validation
- SQL injection prevention through MongoDB
- Environment variable protection
- Error message sanitization

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check if MongoDB is running
   - Verify connection string in .env
   - Check network connectivity

2. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python version compatibility
   - Verify virtual environment activation

3. **Tool Not Found**
   - Restart the MCP server
   - Check tool registration in main.py
   - Verify MCP client configuration

4. **Validation Errors**
   - Check input data format
   - Verify required fields
   - Check data type compatibility

### Debug Mode

Enable debug logging by setting:
```env
LOG_LEVEL=DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Check the documentation
- Review error logs
- Create an issue in the repository

## Changelog

### Version 1.0.0
- Initial release
- Complete CRUD operations for all modules
- Analytics and reporting capabilities
- CSV/JSON export functionality
- Comprehensive validation and error handling
