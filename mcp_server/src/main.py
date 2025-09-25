"""
Main MCP Server implementation for CSE-AIML ERP System.
"""
import asyncio
import logging
import sys
from typing import Any, Dict, List
from mcp.server import Server
from mcp.server.models import Tool
from mcp.types import Resource, TextContent

# Import configuration and database
from .config import get_mcp_server_name, get_settings
from .database import get_database, get_db_operations

# Import all tool modules
from .tools.students import get_student_tools
from .tools.faculties import get_faculty_tools
from .tools.courses import get_course_tools
from .tools.leaves import get_leave_tools
from .tools.timetable import get_timetable_tools
from .tools.analytics import get_analytics_tools
from .tools.reports import get_report_tools

# Import individual tool functions
from .tools.students import (
    get_students, get_student_by_id, create_student, update_student,
    delete_student, search_students, get_students_by_year, get_students_by_batch
)
from .tools.faculties import (
    get_faculties, get_faculty_by_id, create_faculty, update_faculty,
    delete_faculty, search_faculties, assign_subjects_to_faculty, get_faculty_workload
)
from .tools.courses import (
    get_courses, get_course_by_id, create_course, update_course,
    delete_course, search_courses, assign_faculty_to_course, get_courses_by_semester, get_course_statistics
)
from .tools.leaves import (
    get_leaves, get_leave_by_id, create_leave, update_leave,
    delete_leave, approve_leave, reject_leave, get_leaves_by_student, get_pending_leaves, get_leave_statistics
)
from .tools.timetable import (
    get_timetable, get_timetable_by_day, create_timetable_slot, update_timetable_slot,
    delete_timetable_slot, get_faculty_schedule, check_room_availability, get_free_periods
)
from .tools.analytics import (
    get_enrollment_stats, get_attendance_summary, get_leave_analytics,
    get_faculty_workload_report, get_course_popularity, get_demographic_analysis, generate_academic_report
)
from .tools.reports import (
    generate_student_list, generate_faculty_directory, generate_course_catalog,
    generate_leave_report, generate_timetable_report, export_data_csv, generate_summary_dashboard
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CSEAIMLERPMServer:
    """CSE-AIML ERP MCP Server implementation."""
    
    def __init__(self):
        self.server = Server(get_mcp_server_name())
        self.settings = get_settings()
        self._setup_server()
    
    def _setup_server(self):
        """Set up the MCP server with all tools and resources."""
        # Register all tools
        self._register_tools()
        
        # Register resources
        self._register_resources()
        
        # Set up error handling
        self.server.on_error = self._handle_error
    
    def _register_tools(self):
        """Register all MCP tools."""
        # Student management tools
        student_tools = get_student_tools()
        for tool in student_tools:
            self.server.list_tools().append(tool)
        
        # Faculty management tools
        faculty_tools = get_faculty_tools()
        for tool in faculty_tools:
            self.server.list_tools().append(tool)
        
        # Course management tools
        course_tools = get_course_tools()
        for tool in course_tools:
            self.server.list_tools().append(tool)
        
        # Leave management tools
        leave_tools = get_leave_tools()
        for tool in leave_tools:
            self.server.list_tools().append(tool)
        
        # Timetable management tools
        timetable_tools = get_timetable_tools()
        for tool in timetable_tools:
            self.server.list_tools().append(tool)
        
        # Analytics tools
        analytics_tools = get_analytics_tools()
        for tool in analytics_tools:
            self.server.list_tools().append(tool)
        
        # Report generation tools
        report_tools = get_report_tools()
        for tool in report_tools:
            self.server.list_tools().append(tool)
        
        # Register tool handlers
        self._register_tool_handlers()
    
    def _register_tool_handlers(self):
        """Register handlers for all tools."""
        # Student tools
        @self.server.call_tool()
        async def get_students_tool(page: int = 1, page_size: int = 50, year: str = None, batch: str = None, sort_by: str = "roll", sort_order: str = "asc") -> List[TextContent]:
            result = await get_students(page, page_size, year, batch, sort_by, sort_order)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def get_student_by_id_tool(student_id: str) -> List[TextContent]:
            result = await get_student_by_id(student_id)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def create_student_tool(roll: str, full_name: str, email: str, phone: str = None, year: str = None, batch: str = None, date_of_birth: str = None) -> List[TextContent]:
            result = await create_student(roll, full_name, email, phone, year, batch, date_of_birth)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def update_student_tool(student_id: str, roll: str = None, full_name: str = None, email: str = None, phone: str = None, year: str = None, batch: str = None, date_of_birth: str = None) -> List[TextContent]:
            result = await update_student(student_id, roll, full_name, email, phone, year, batch, date_of_birth)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def delete_student_tool(student_id: str) -> List[TextContent]:
            result = await delete_student(student_id)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def search_students_tool(query: str, page: int = 1, page_size: int = 50, search_fields: List[str] = None) -> List[TextContent]:
            result = await search_students(query, page, page_size, search_fields)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def get_students_by_year_tool(year: str, page: int = 1, page_size: int = 50) -> List[TextContent]:
            result = await get_students_by_year(year, page, page_size)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def get_students_by_batch_tool(batch: str, page: int = 1, page_size: int = 50) -> List[TextContent]:
            result = await get_students_by_batch(batch, page, page_size)
            return [TextContent(type="text", text=str(result))]
        
        # Faculty tools
        @self.server.call_tool()
        async def get_faculties_tool(page: int = 1, page_size: int = 50, designation: str = None, sort_by: str = "fullName", sort_order: str = "asc") -> List[TextContent]:
            result = await get_faculties(page, page_size, designation, sort_by, sort_order)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def get_faculty_by_id_tool(faculty_id: str) -> List[TextContent]:
            result = await get_faculty_by_id(faculty_id)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def create_faculty_tool(employee_id: str, full_name: str, email: str, designation: str, phone: str = None, subjects: List[str] = None) -> List[TextContent]:
            result = await create_faculty(employee_id, full_name, email, designation, phone, subjects)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def update_faculty_tool(faculty_id: str, employee_id: str = None, full_name: str = None, email: str = None, designation: str = None, phone: str = None, subjects: List[str] = None) -> List[TextContent]:
            result = await update_faculty(faculty_id, employee_id, full_name, email, designation, phone, subjects)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def delete_faculty_tool(faculty_id: str) -> List[TextContent]:
            result = await delete_faculty(faculty_id)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def search_faculties_tool(query: str, page: int = 1, page_size: int = 50, search_fields: List[str] = None) -> List[TextContent]:
            result = await search_faculties(query, page, page_size, search_fields)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def assign_subjects_to_faculty_tool(faculty_id: str, subjects: List[str]) -> List[TextContent]:
            result = await assign_subjects_to_faculty(faculty_id, subjects)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def get_faculty_workload_tool(faculty_id: str) -> List[TextContent]:
            result = await get_faculty_workload(faculty_id)
            return [TextContent(type="text", text=str(result))]
        
        # Course tools
        @self.server.call_tool()
        async def get_courses_tool(page: int = 1, page_size: int = 50, semester: int = None, sort_by: str = "code", sort_order: str = "asc") -> List[TextContent]:
            result = await get_courses(page, page_size, semester, sort_by, sort_order)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def get_course_by_id_tool(course_id: str) -> List[TextContent]:
            result = await get_course_by_id(course_id)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def create_course_tool(code: str, title: str, credits: float, semester: int, description: str = None, faculty_in_charge: str = None) -> List[TextContent]:
            result = await create_course(code, title, credits, semester, description, faculty_in_charge)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def update_course_tool(course_id: str, code: str = None, title: str = None, credits: float = None, semester: int = None, description: str = None, faculty_in_charge: str = None) -> List[TextContent]:
            result = await update_course(course_id, code, title, credits, semester, description, faculty_in_charge)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def delete_course_tool(course_id: str) -> List[TextContent]:
            result = await delete_course(course_id)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def search_courses_tool(query: str, page: int = 1, page_size: int = 50, search_fields: List[str] = None) -> List[TextContent]:
            result = await search_courses(query, page, page_size, search_fields)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def assign_faculty_to_course_tool(course_id: str, faculty_id: str) -> List[TextContent]:
            result = await assign_faculty_to_course(course_id, faculty_id)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def get_courses_by_semester_tool(semester: int, page: int = 1, page_size: int = 50) -> List[TextContent]:
            result = await get_courses_by_semester(semester, page, page_size)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def get_course_statistics_tool() -> List[TextContent]:
            result = await get_course_statistics()
            return [TextContent(type="text", text=str(result))]
        
        # Leave tools
        @self.server.call_tool()
        async def get_leaves_tool(page: int = 1, page_size: int = 50, status: str = None, sort_by: str = "createdAt", sort_order: str = "desc") -> List[TextContent]:
            result = await get_leaves(page, page_size, status, sort_by, sort_order)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def get_leave_by_id_tool(leave_id: str) -> List[TextContent]:
            result = await get_leave_by_id(leave_id)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def create_leave_tool(student_id: str, start_date: str, end_date: str, reason: str, status: str = "pending") -> List[TextContent]:
            result = await create_leave(student_id, start_date, end_date, reason, status)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def update_leave_tool(leave_id: str, start_date: str = None, end_date: str = None, reason: str = None, status: str = None, handled_by: str = None, remarks: str = None) -> List[TextContent]:
            result = await update_leave(leave_id, start_date, end_date, reason, status, handled_by, remarks)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def delete_leave_tool(leave_id: str) -> List[TextContent]:
            result = await delete_leave(leave_id)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def approve_leave_tool(leave_id: str, handled_by: str, remarks: str = None) -> List[TextContent]:
            result = await approve_leave(leave_id, handled_by, remarks)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def reject_leave_tool(leave_id: str, handled_by: str, remarks: str) -> List[TextContent]:
            result = await reject_leave(leave_id, handled_by, remarks)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def get_leaves_by_student_tool(student_id: str, page: int = 1, page_size: int = 50, status: str = None) -> List[TextContent]:
            result = await get_leaves_by_student(student_id, page, page_size, status)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def get_pending_leaves_tool(page: int = 1, page_size: int = 50) -> List[TextContent]:
            result = await get_pending_leaves(page, page_size)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def get_leave_statistics_tool() -> List[TextContent]:
            result = await get_leave_statistics()
            return [TextContent(type="text", text=str(result))]
        
        # Timetable tools
        @self.server.call_tool()
        async def get_timetable_tool(page: int = 1, page_size: int = 50, day_of_week: str = None, sort_by: str = "dayOfWeek", sort_order: str = "asc") -> List[TextContent]:
            result = await get_timetable(page, page_size, day_of_week, sort_by, sort_order)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def get_timetable_by_day_tool(day_of_week: str) -> List[TextContent]:
            result = await get_timetable_by_day(day_of_week)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def create_timetable_slot_tool(day_of_week: str, period: int, start_time: str, end_time: str, slot_type: str, course_code: str = None, faculty_id: str = None, room: str = None) -> List[TextContent]:
            result = await create_timetable_slot(day_of_week, period, start_time, end_time, slot_type, course_code, faculty_id, room)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def update_timetable_slot_tool(day_of_week: str, period: int, start_time: str = None, end_time: str = None, slot_type: str = None, course_code: str = None, faculty_id: str = None, room: str = None) -> List[TextContent]:
            result = await update_timetable_slot(day_of_week, period, start_time, end_time, slot_type, course_code, faculty_id, room)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def delete_timetable_slot_tool(day_of_week: str, period: int) -> List[TextContent]:
            result = await delete_timetable_slot(day_of_week, period)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def get_faculty_schedule_tool(faculty_id: str) -> List[TextContent]:
            result = await get_faculty_schedule(faculty_id)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def check_room_availability_tool(room: str, day_of_week: str = None, start_time: str = None, end_time: str = None) -> List[TextContent]:
            result = await check_room_availability(room, day_of_week, start_time, end_time)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def get_free_periods_tool(day_of_week: str = None, faculty_id: str = None, room: str = None) -> List[TextContent]:
            result = await get_free_periods(day_of_week, faculty_id, room)
            return [TextContent(type="text", text=str(result))]
        
        # Analytics tools
        @self.server.call_tool()
        async def get_enrollment_stats_tool() -> List[TextContent]:
            result = await get_enrollment_stats()
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def get_attendance_summary_tool() -> List[TextContent]:
            result = await get_attendance_summary()
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def get_leave_analytics_tool() -> List[TextContent]:
            result = await get_leave_analytics()
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def get_faculty_workload_report_tool() -> List[TextContent]:
            result = await get_faculty_workload_report()
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def get_course_popularity_tool() -> List[TextContent]:
            result = await get_course_popularity()
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def get_demographic_analysis_tool() -> List[TextContent]:
            result = await get_demographic_analysis()
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def generate_academic_report_tool() -> List[TextContent]:
            result = await generate_academic_report()
            return [TextContent(type="text", text=str(result))]
        
        # Report tools
        @self.server.call_tool()
        async def generate_student_list_tool(year: str = None, batch: str = None, format_type: str = "json") -> List[TextContent]:
            result = await generate_student_list(year, batch, format_type)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def generate_faculty_directory_tool(designation: str = None, format_type: str = "json") -> List[TextContent]:
            result = await generate_faculty_directory(designation, format_type)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def generate_course_catalog_tool(semester: int = None, format_type: str = "json") -> List[TextContent]:
            result = await generate_course_catalog(semester, format_type)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def generate_leave_report_tool(status: str = None, student_id: str = None, start_date: str = None, end_date: str = None, format_type: str = "json") -> List[TextContent]:
            result = await generate_leave_report(status, student_id, start_date, end_date, format_type)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def generate_timetable_report_tool(day_of_week: str = None, format_type: str = "json") -> List[TextContent]:
            result = await generate_timetable_report(day_of_week, format_type)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def export_data_csv_tool(collection_name: str, filters: Dict[str, Any] = None, limit: int = None) -> List[TextContent]:
            result = await export_data_csv(collection_name, filters, limit)
            return [TextContent(type="text", text=str(result))]
        
        @self.server.call_tool()
        async def generate_summary_dashboard_tool() -> List[TextContent]:
            result = await generate_summary_dashboard()
            return [TextContent(type="text", text=str(result))]
    
    def _register_resources(self):
        """Register MCP resources."""
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            return [
                Resource(
                    uri="cse-aiml-erp://database/info",
                    name="Database Information",
                    description="Information about the CSE-AIML ERP database structure and collections"
                ),
                Resource(
                    uri="cse-aiml-erp://system/status",
                    name="System Status",
                    description="Current system status and health information"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            if uri == "cse-aiml-erp://database/info":
                return self._get_database_info()
            elif uri == "cse-aiml-erp://system/status":
                return await self._get_system_status()
            else:
                raise ValueError(f"Unknown resource: {uri}")
    
    def _get_database_info(self) -> str:
        """Get database information."""
        return """
CSE-AIML ERP Database Structure:

Collections:
1. students - Student records
   - roll: Student roll number (e.g., CSE001)
   - fullName: Student full name
   - email: Student email address
   - phone: Student phone number
   - year: Academic year
   - batch: Batch identifier
   - dateOfBirth: Date of birth
   - createdAt: Creation timestamp
   - updatedAt: Last update timestamp

2. faculties - Faculty records
   - employeeId: Faculty employee ID (e.g., EMP001)
   - fullName: Faculty full name
   - email: Faculty email address
   - phone: Faculty phone number
   - designation: Faculty designation/position
   - subjects: List of subjects taught
   - createdAt: Creation timestamp
   - updatedAt: Last update timestamp

3. courses - Course records
   - code: Course code (e.g., CS101)
   - title: Course title
   - credits: Number of credits
   - semester: Semester number
   - facultyInCharge: Faculty ObjectId in charge
   - description: Course description
   - createdAt: Creation timestamp
   - updatedAt: Last update timestamp

4. leaves - Leave applications
   - studentId: Student ObjectId
   - startDate: Leave start date
   - endDate: Leave end date
   - reason: Leave reason
   - status: Leave status (pending, approved, rejected, cancelled)
   - handledBy: Faculty ObjectId who handled
   - remarks: Additional remarks
   - createdAt: Creation timestamp
   - updatedAt: Last update timestamp

5. timetables - Timetable records
   - dayOfWeek: Day of week
   - slots: Array of time slots
     - period: Period number
     - startTime: Start time
     - endTime: End time
     - type: Slot type
     - courseCode: Course code
     - facultyId: Faculty ObjectId
     - room: Room number/name
   - createdAt: Creation timestamp
   - updatedAt: Last update timestamp
"""
    
    async def _get_system_status(self) -> str:
        """Get system status."""
        try:
            # Get database operations
            db_ops = await get_db_operations()
            
            # Get basic counts
            total_students = await db_ops.count_documents("students", {})
            total_faculty = await db_ops.count_documents("faculties", {})
            total_courses = await db_ops.count_documents("courses", {})
            total_leaves = await db_ops.count_documents("leaves", {})
            pending_leaves = await db_ops.count_documents("leaves", {"status": "pending"})
            
            status = f"""
CSE-AIML ERP System Status:

Database Connection: Connected
Server Status: Running
Last Updated: {datetime.now().isoformat()}

Record Counts:
- Students: {total_students}
- Faculty: {total_faculty}
- Courses: {total_courses}
- Leave Applications: {total_leaves}
- Pending Leaves: {pending_leaves}

Available Tools: {len(self.server.list_tools())}
Available Resources: {len(self.server.list_resources())}
"""
            return status
            
        except Exception as e:
            return f"System Status: Error - {str(e)}"
    
    async def _handle_error(self, error: Exception) -> None:
        """Handle server errors."""
        logger.error(f"MCP Server Error: {error}")
    
    async def run(self):
        """Run the MCP server."""
        try:
            # Initialize database connection
            await get_database()
            logger.info("Database connection established")
            
            # Start the server
            logger.info(f"Starting CSE-AIML ERP MCP Server: {get_mcp_server_name()}")
            await self.server.run()
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            sys.exit(1)


async def main():
    """Main entry point."""
    server = CSEAIMLERPMServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
