"""
Report generation tools for CSE-AIML ERP MCP Server.
"""
import logging
import csv
import io
from typing import Any, Dict, List, Optional
from datetime import datetime
from mcp.server.models import Tool

from ..database import get_db_operations
from ..utils.formatters import (
    format_success_response, format_error_response, format_csv_row,
    format_student_data, format_faculty_data, format_course_data,
    format_leave_data, format_timetable_data
)

logger = logging.getLogger(__name__)


async def generate_student_list(
    year: Optional[str] = None,
    batch: Optional[str] = None,
    format_type: str = "json"
) -> Dict[str, Any]:
    """
    Generate formatted student roster.
    
    Args:
        year: Filter by academic year (optional)
        batch: Filter by batch (optional)
        format_type: Output format - json or csv (default: json)
    """
    try:
        # Get database operations
        db_ops = await get_db_operations()
        
        # Build query
        query = {}
        if year:
            query["year"] = year
        if batch:
            query["batch"] = batch
        
        # Get students
        students = await db_ops.find_many("students", query=query, sort=[("roll", 1)])
        
        if format_type.lower() == "csv":
            # Generate CSV format
            headers = ["id", "roll", "fullName", "email", "phone", "year", "batch", "dateOfBirth", "createdAt"]
            csv_rows = []
            
            for student in students:
                row = format_csv_row(student, headers)
                csv_rows.append(row)
            
            # Create CSV string
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            writer.writerows(csv_rows)
            csv_content = output.getvalue()
            output.close()
            
            return format_success_response(
                {
                    "format": "csv",
                    "content": csv_content,
                    "filename": f"student_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "record_count": len(students)
                },
                f"Student list generated in CSV format with {len(students)} records"
            )
        else:
            # Generate JSON format
            formatted_students = [format_student_data(student) for student in students]
            
            return format_success_response(
                {
                    "format": "json",
                    "students": formatted_students,
                    "record_count": len(students),
                    "filters": {"year": year, "batch": batch}
                },
                f"Student list generated in JSON format with {len(students)} records"
            )
        
    except Exception as e:
        logger.error(f"Error generating student list: {e}")
        return format_error_response(e, "Failed to generate student list")


async def generate_faculty_directory(
    designation: Optional[str] = None,
    format_type: str = "json"
) -> Dict[str, Any]:
    """
    Generate faculty contact information directory.
    
    Args:
        designation: Filter by designation (optional)
        format_type: Output format - json or csv (default: json)
    """
    try:
        # Get database operations
        db_ops = await get_db_operations()
        
        # Build query
        query = {}
        if designation:
            query["designation"] = {"$regex": designation, "$options": "i"}
        
        # Get faculty
        faculties = await db_ops.find_many("faculties", query=query, sort=[("fullName", 1)])
        
        if format_type.lower() == "csv":
            # Generate CSV format
            headers = ["id", "employeeId", "fullName", "email", "phone", "designation", "subjects"]
            csv_rows = []
            
            for faculty in faculties:
                row = format_csv_row(faculty, headers)
                # Handle subjects array
                if "subjects" in row and isinstance(faculty.get("subjects"), list):
                    row["subjects"] = "; ".join(faculty.get("subjects", []))
                csv_rows.append(row)
            
            # Create CSV string
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            writer.writerows(csv_rows)
            csv_content = output.getvalue()
            output.close()
            
            return format_success_response(
                {
                    "format": "csv",
                    "content": csv_content,
                    "filename": f"faculty_directory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "record_count": len(faculties)
                },
                f"Faculty directory generated in CSV format with {len(faculties)} records"
            )
        else:
            # Generate JSON format
            formatted_faculties = [format_faculty_data(faculty) for faculty in faculties]
            
            return format_success_response(
                {
                    "format": "json",
                    "faculties": formatted_faculties,
                    "record_count": len(faculties),
                    "filters": {"designation": designation}
                },
                f"Faculty directory generated in JSON format with {len(faculties)} records"
            )
        
    except Exception as e:
        logger.error(f"Error generating faculty directory: {e}")
        return format_error_response(e, "Failed to generate faculty directory")


async def generate_course_catalog(
    semester: Optional[int] = None,
    format_type: str = "json"
) -> Dict[str, Any]:
    """
    Generate complete course listing.
    
    Args:
        semester: Filter by semester (optional)
        format_type: Output format - json or csv (default: json)
    """
    try:
        # Get database operations
        db_ops = await get_db_operations()
        
        # Build query
        query = {}
        if semester:
            query["semester"] = semester
        
        # Get courses with faculty information
        courses = await db_ops.aggregate("courses", [
            {"$match": query},
            {"$lookup": {
                "from": "faculties",
                "localField": "facultyInCharge",
                "foreignField": "_id",
                "as": "faculty"
            }},
            {"$project": {
                "code": 1,
                "title": 1,
                "credits": 1,
                "semester": 1,
                "description": 1,
                "facultyInCharge": 1,
                "faculty_name": {"$arrayElemAt": ["$faculty.fullName", 0]},
                "faculty_employee_id": {"$arrayElemAt": ["$faculty.employeeId", 0]},
                "createdAt": 1,
                "updatedAt": 1
            }},
            {"$sort": {"semester": 1, "code": 1}}
        ])
        
        if format_type.lower() == "csv":
            # Generate CSV format
            headers = ["id", "code", "title", "credits", "semester", "description", "faculty_name", "faculty_employee_id"]
            csv_rows = []
            
            for course in courses:
                row = format_csv_row(course, headers)
                csv_rows.append(row)
            
            # Create CSV string
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            writer.writerows(csv_rows)
            csv_content = output.getvalue()
            output.close()
            
            return format_success_response(
                {
                    "format": "csv",
                    "content": csv_content,
                    "filename": f"course_catalog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "record_count": len(courses)
                },
                f"Course catalog generated in CSV format with {len(courses)} records"
            )
        else:
            # Generate JSON format
            formatted_courses = [format_course_data(course) for course in courses]
            
            return format_success_response(
                {
                    "format": "json",
                    "courses": formatted_courses,
                    "record_count": len(courses),
                    "filters": {"semester": semester}
                },
                f"Course catalog generated in JSON format with {len(courses)} records"
            )
        
    except Exception as e:
        logger.error(f"Error generating course catalog: {e}")
        return format_error_response(e, "Failed to generate course catalog")


async def generate_leave_report(
    status: Optional[str] = None,
    student_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    format_type: str = "json"
) -> Dict[str, Any]:
    """
    Generate leave status report.
    
    Args:
        status: Filter by status (optional)
        student_id: Filter by student ID (optional)
        start_date: Filter by start date (optional)
        end_date: Filter by end date (optional)
        format_type: Output format - json or csv (default: json)
    """
    try:
        # Get database operations
        db_ops = await get_db_operations()
        
        # Build query
        query = {}
        if status:
            query["status"] = status.lower()
        if student_id:
            query["studentId"] = student_id
        if start_date:
            query["startDate"] = {"$gte": start_date}
        if end_date:
            query["endDate"] = {"$lte": end_date}
        
        # Get leaves with student information
        leaves = await db_ops.aggregate("leaves", [
            {"$match": query},
            {"$lookup": {
                "from": "students",
                "localField": "studentId",
                "foreignField": "_id",
                "as": "student"
            }},
            {"$lookup": {
                "from": "faculties",
                "localField": "handledBy",
                "foreignField": "_id",
                "as": "handler"
            }},
            {"$project": {
                "studentId": 1,
                "startDate": 1,
                "endDate": 1,
                "reason": 1,
                "status": 1,
                "handledBy": 1,
                "remarks": 1,
                "createdAt": 1,
                "student_name": {"$arrayElemAt": ["$student.fullName", 0]},
                "student_roll": {"$arrayElemAt": ["$student.roll", 0]},
                "handler_name": {"$arrayElemAt": ["$handler.fullName", 0]},
                "handler_employee_id": {"$arrayElemAt": ["$handler.employeeId", 0]}
            }},
            {"$sort": {"createdAt": -1}}
        ])
        
        if format_type.lower() == "csv":
            # Generate CSV format
            headers = ["id", "student_roll", "student_name", "startDate", "endDate", "reason", "status", "handler_name", "handler_employee_id", "remarks", "createdAt"]
            csv_rows = []
            
            for leave in leaves:
                row = format_csv_row(leave, headers)
                csv_rows.append(row)
            
            # Create CSV string
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            writer.writerows(csv_rows)
            csv_content = output.getvalue()
            output.close()
            
            return format_success_response(
                {
                    "format": "csv",
                    "content": csv_content,
                    "filename": f"leave_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "record_count": len(leaves)
                },
                f"Leave report generated in CSV format with {len(leaves)} records"
            )
        else:
            # Generate JSON format
            formatted_leaves = [format_leave_data(leave) for leave in leaves]
            
            return format_success_response(
                {
                    "format": "json",
                    "leaves": formatted_leaves,
                    "record_count": len(leaves),
                    "filters": {"status": status, "student_id": student_id, "start_date": start_date, "end_date": end_date}
                },
                f"Leave report generated in JSON format with {len(leaves)} records"
            )
        
    except Exception as e:
        logger.error(f"Error generating leave report: {e}")
        return format_error_response(e, "Failed to generate leave report")


async def generate_timetable_report(
    day_of_week: Optional[str] = None,
    format_type: str = "json"
) -> Dict[str, Any]:
    """
    Generate formatted timetable report.
    
    Args:
        day_of_week: Filter by day of week (optional)
        format_type: Output format - json or csv (default: json)
    """
    try:
        # Get database operations
        db_ops = await get_db_operations()
        
        # Build query
        query = {}
        if day_of_week:
            query["dayOfWeek"] = day_of_week.lower()
        
        # Get timetable
        timetables = await db_ops.find_many("timetables", query=query, sort=[("dayOfWeek", 1)])
        
        if format_type.lower() == "csv":
            # Generate CSV format
            headers = ["dayOfWeek", "period", "startTime", "endTime", "type", "courseCode", "facultyId", "room"]
            csv_rows = []
            
            for timetable in timetables:
                for slot in timetable.get("slots", []):
                    row = {
                        "dayOfWeek": timetable.get("dayOfWeek"),
                        **format_csv_row(slot, ["period", "startTime", "endTime", "type", "courseCode", "facultyId", "room"])
                    }
                    csv_rows.append(row)
            
            # Create CSV string
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            writer.writerows(csv_rows)
            csv_content = output.getvalue()
            output.close()
            
            return format_success_response(
                {
                    "format": "csv",
                    "content": csv_content,
                    "filename": f"timetable_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "record_count": len(csv_rows)
                },
                f"Timetable report generated in CSV format with {len(csv_rows)} slots"
            )
        else:
            # Generate JSON format
            formatted_timetables = [format_timetable_data(timetable) for timetable in timetables]
            
            return format_success_response(
                {
                    "format": "json",
                    "timetables": formatted_timetables,
                    "record_count": len(timetables),
                    "filters": {"day_of_week": day_of_week}
                },
                f"Timetable report generated in JSON format with {len(timetables)} days"
            )
        
    except Exception as e:
        logger.error(f"Error generating timetable report: {e}")
        return format_error_response(e, "Failed to generate timetable report")


async def export_data_csv(
    collection_name: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Export collection data to CSV format.
    
    Args:
        collection_name: Name of collection to export
        filters: Optional filters to apply
        limit: Optional limit on number of records
    """
    try:
        # Validate collection name
        valid_collections = ["students", "faculties", "courses", "leaves", "timetables"]
        if collection_name not in valid_collections:
            return format_error_response(
                ValueError("Invalid collection"),
                f"Invalid collection name. Valid collections: {', '.join(valid_collections)}"
            )
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get data
        query = filters or {}
        data = await db_ops.find_many(
            collection_name,
            query=query,
            limit=limit,
            sort=[("_id", 1)]
        )
        
        if not data:
            return format_error_response(
                ValueError("No data found"),
                f"No data found in {collection_name} with the specified filters"
            )
        
        # Get headers from first record
        headers = list(data[0].keys())
        
        # Generate CSV rows
        csv_rows = []
        for record in data:
            row = format_csv_row(record, headers)
            csv_rows.append(row)
        
        # Create CSV string
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        writer.writerows(csv_rows)
        csv_content = output.getvalue()
        output.close()
        
        return format_success_response(
            {
                "collection": collection_name,
                "format": "csv",
                "content": csv_content,
                "filename": f"{collection_name}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "record_count": len(data),
                "filters_applied": filters
            },
            f"Data exported from {collection_name} with {len(data)} records"
        )
        
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return format_error_response(e, "Failed to export data")


async def generate_summary_dashboard() -> Dict[str, Any]:
    """
    Generate dashboard data compilation with key metrics.
    """
    try:
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get key metrics
        total_students = await db_ops.count_documents("students", {})
        total_faculty = await db_ops.count_documents("faculties", {})
        total_courses = await db_ops.count_documents("courses", {})
        total_leaves = await db_ops.count_documents("leaves", {})
        
        # Get pending leaves count
        pending_leaves = await db_ops.count_documents("leaves", {"status": "pending"})
        
        # Get courses without faculty
        courses_without_faculty = await db_ops.count_documents("courses", {"facultyInCharge": {"$exists": False}})
        
        # Get recent activity (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_students = await db_ops.count_documents("students", {"createdAt": {"$gte": seven_days_ago}})
        recent_leaves = await db_ops.count_documents("leaves", {"createdAt": {"$gte": seven_days_ago}})
        
        # Get leave status distribution
        leave_status_stats = await db_ops.aggregate("leaves", [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ])
        
        # Get student year distribution
        year_stats = await db_ops.aggregate("students", [
            {"$group": {"_id": "$year", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ])
        
        dashboard_data = {
            "generated_at": datetime.now().isoformat(),
            "key_metrics": {
                "total_students": total_students,
                "total_faculty": total_faculty,
                "total_courses": total_courses,
                "total_leaves": total_leaves,
                "pending_leaves": pending_leaves,
                "courses_without_faculty": courses_without_faculty
            },
            "recent_activity": {
                "new_students_7_days": recent_students,
                "new_leaves_7_days": recent_leaves
            },
            "distributions": {
                "leave_status": {stat["_id"]: stat["count"] for stat in leave_status_stats},
                "student_years": {stat["_id"]: stat["count"] for stat in year_stats if stat["_id"]}
            },
            "alerts": {
                "pending_leaves_count": pending_leaves,
                "courses_without_faculty_count": courses_without_faculty,
                "has_alerts": pending_leaves > 0 or courses_without_faculty > 0
            }
        }
        
        return format_success_response(
            dashboard_data,
            "Summary dashboard data generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating summary dashboard: {e}")
        return format_error_response(e, "Failed to generate summary dashboard")


# MCP Tool definitions
def get_report_tools() -> List[Tool]:
    """Get all report generation tools."""
    return [
        Tool(
            name="generate_student_list",
            description="Generate formatted student roster",
            inputSchema={
                "type": "object",
                "properties": {
                    "year": {"type": "string", "description": "Filter by academic year (optional)"},
                    "batch": {"type": "string", "description": "Filter by batch (optional)"},
                    "format_type": {"type": "string", "enum": ["json", "csv"], "default": "json", "description": "Output format"}
                }
            }
        ),
        Tool(
            name="generate_faculty_directory",
            description="Generate faculty contact information directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "designation": {"type": "string", "description": "Filter by designation (optional)"},
                    "format_type": {"type": "string", "enum": ["json", "csv"], "default": "json", "description": "Output format"}
                }
            }
        ),
        Tool(
            name="generate_course_catalog",
            description="Generate complete course listing",
            inputSchema={
                "type": "object",
                "properties": {
                    "semester": {"type": "integer", "description": "Filter by semester (optional)"},
                    "format_type": {"type": "string", "enum": ["json", "csv"], "default": "json", "description": "Output format"}
                }
            }
        ),
        Tool(
            name="generate_leave_report",
            description="Generate leave status report",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["pending", "approved", "rejected", "cancelled"], "description": "Filter by status (optional)"},
                    "student_id": {"type": "string", "description": "Filter by student ID (optional)"},
                    "start_date": {"type": "string", "description": "Filter by start date (optional)"},
                    "end_date": {"type": "string", "description": "Filter by end date (optional)"},
                    "format_type": {"type": "string", "enum": ["json", "csv"], "default": "json", "description": "Output format"}
                }
            }
        ),
        Tool(
            name="generate_timetable_report",
            description="Generate formatted timetable report",
            inputSchema={
                "type": "object",
                "properties": {
                    "day_of_week": {"type": "string", "enum": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"], "description": "Filter by day of week (optional)"},
                    "format_type": {"type": "string", "enum": ["json", "csv"], "default": "json", "description": "Output format"}
                }
            }
        ),
        Tool(
            name="export_data_csv",
            description="Export collection data to CSV format",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_name": {"type": "string", "enum": ["students", "faculties", "courses", "leaves", "timetables"], "description": "Name of collection to export"},
                    "filters": {"type": "object", "description": "Optional filters to apply"},
                    "limit": {"type": "integer", "description": "Optional limit on number of records"}
                },
                "required": ["collection_name"]
            }
        ),
        Tool(
            name="generate_summary_dashboard",
            description="Generate dashboard data compilation with key metrics",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]
