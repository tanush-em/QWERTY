"""
Faculty management tools for CSE-AIML ERP MCP Server.
"""
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from mcp import Tool
from pymongo.errors import DuplicateKeyError

from database import get_db_operations
from utils.validators import (
    validate_faculty_data, validate_object_id, validate_pagination_params,
    validate_search_query, validate_employee_id
)
from utils.formatters import (
    format_faculty_data, format_success_response, format_error_response,
    format_paginated_response
)

logger = logging.getLogger(__name__)


async def get_faculties(
    page: int = 1,
    page_size: int = 50,
    designation: Optional[str] = None,
    sort_by: str = "fullName",
    sort_order: str = "asc"
) -> Dict[str, Any]:
    """
    Get list of faculty members with optional filtering and pagination.
    
    Args:
        page: Page number (default: 1)
        page_size: Number of items per page (default: 50)
        designation: Filter by designation
        sort_by: Field to sort by (default: fullName)
        sort_order: Sort order - asc or desc (default: asc)
    """
    try:
        # Validate pagination parameters
        page, page_size = validate_pagination_params(page, page_size)
        
        # Build query
        query = {}
        if designation:
            query["designation"] = {"$regex": designation, "$options": "i"}
        
        # Build sort
        sort_direction = 1 if sort_order.lower() == "asc" else -1
        sort = [(sort_by, sort_direction)]
        
        # Calculate skip
        skip = (page - 1) * page_size
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get faculties
        faculties = await db_ops.find_many(
            "faculties",
            query=query,
            skip=skip,
            limit=page_size,
            sort=sort
        )
        
        # Get total count
        total_count = await db_ops.count_documents("faculties", query)
        
        # Format faculties data
        formatted_faculties = [format_faculty_data(faculty) for faculty in faculties]
        
        return format_paginated_response(
            formatted_faculties,
            page,
            page_size,
            total_count,
            f"Retrieved {len(formatted_faculties)} faculty members"
        )
        
    except Exception as e:
        logger.error(f"Error getting faculties: {e}")
        return format_error_response(e, "Failed to retrieve faculties")


async def get_faculty_by_id(faculty_id: str) -> Dict[str, Any]:
    """
    Get specific faculty member by ID.
    
    Args:
        faculty_id: Faculty ObjectId
    """
    try:
        # Validate faculty ID
        if not validate_object_id(faculty_id):
            return format_error_response(
                ValueError("Invalid faculty ID format"),
                "Invalid faculty ID format"
            )
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get faculty
        faculty = await db_ops.find_one("faculties", {"_id": faculty_id})
        
        if not faculty:
            return format_error_response(
                ValueError("Faculty not found"),
                "Faculty not found"
            )
        
        # Format faculty data
        formatted_faculty = format_faculty_data(faculty)
        
        return format_success_response(
            formatted_faculty,
            "Faculty retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting faculty by ID: {e}")
        return format_error_response(e, "Failed to retrieve faculty")


async def create_faculty(
    employee_id: str,
    full_name: str,
    email: str,
    designation: str,
    phone: Optional[str] = None,
    subjects: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create new faculty member record.
    
    Args:
        employee_id: Faculty employee ID (e.g., EMP001)
        full_name: Faculty full name
        email: Faculty email address
        designation: Faculty designation/position
        phone: Faculty phone number (optional)
        subjects: List of subjects taught (optional)
    """
    try:
        # Prepare faculty data
        faculty_data = {
            "employeeId": employee_id,
            "fullName": full_name,
            "email": email,
            "designation": designation,
            "phone": phone,
            "subjects": subjects or [],
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        # Validate faculty data
        validation_errors = validate_faculty_data(faculty_data)
        if validation_errors:
            return format_error_response(
                ValueError("Validation failed"),
                "Validation failed",
                errors=[str(error) for error_list in validation_errors.values() for error in error_list]
            )
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Check if faculty with same employee ID already exists
        existing_faculty = await db_ops.find_one("faculties", {"employeeId": employee_id})
        if existing_faculty:
            return format_error_response(
                ValueError("Faculty already exists"),
                f"Faculty with employee ID {employee_id} already exists"
            )
        
        # Create faculty
        faculty_id = await db_ops.insert_one("faculties", faculty_data)
        
        # Get created faculty
        created_faculty = await db_ops.find_one("faculties", {"_id": faculty_id})
        formatted_faculty = format_faculty_data(created_faculty)
        
        return format_success_response(
            formatted_faculty,
            f"Faculty {employee_id} created successfully"
        )
        
    except DuplicateKeyError as e:
        logger.error(f"Duplicate key error creating faculty: {e}")
        return format_error_response(e, "Faculty with this employee ID already exists")
    except Exception as e:
        logger.error(f"Error creating faculty: {e}")
        return format_error_response(e, "Failed to create faculty")


async def update_faculty(
    faculty_id: str,
    employee_id: Optional[str] = None,
    full_name: Optional[str] = None,
    email: Optional[str] = None,
    designation: Optional[str] = None,
    phone: Optional[str] = None,
    subjects: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Update existing faculty member record.
    
    Args:
        faculty_id: Faculty ObjectId
        employee_id: Updated employee ID (optional)
        full_name: Updated full name (optional)
        email: Updated email (optional)
        designation: Updated designation (optional)
        phone: Updated phone (optional)
        subjects: Updated subjects list (optional)
    """
    try:
        # Validate faculty ID
        if not validate_object_id(faculty_id):
            return format_error_response(
                ValueError("Invalid faculty ID format"),
                "Invalid faculty ID format"
            )
        
        # Prepare update data
        update_data = {}
        if employee_id is not None:
            update_data["employeeId"] = employee_id
        if full_name is not None:
            update_data["fullName"] = full_name
        if email is not None:
            update_data["email"] = email
        if designation is not None:
            update_data["designation"] = designation
        if phone is not None:
            update_data["phone"] = phone
        if subjects is not None:
            update_data["subjects"] = subjects
        
        if not update_data:
            return format_error_response(
                ValueError("No update data provided"),
                "No update data provided"
            )
        
        update_data["updatedAt"] = datetime.now()
        
        # Validate updated data if employee_id or email is being updated
        if employee_id or email:
            # Get existing faculty to merge with updates
            db_ops = await get_db_operations()
            existing_faculty = await db_ops.find_one("faculties", {"_id": faculty_id})
            
            if not existing_faculty:
                return format_error_response(
                    ValueError("Faculty not found"),
                    "Faculty not found"
                )
            
            # Merge existing data with updates
            merged_data = {**existing_faculty, **update_data}
            validation_errors = validate_faculty_data(merged_data)
            if validation_errors:
                return format_error_response(
                    ValueError("Validation failed"),
                    "Validation failed",
                    errors=[str(error) for error_list in validation_errors.values() for error in error_list]
                )
        
        # Update faculty
        success = await db_ops.update_one(
            "faculties",
            {"_id": faculty_id},
            {"$set": update_data}
        )
        
        if not success:
            return format_error_response(
                ValueError("Update failed"),
                "No changes made to faculty record"
            )
        
        # Get updated faculty
        updated_faculty = await db_ops.find_one("faculties", {"_id": faculty_id})
        formatted_faculty = format_faculty_data(updated_faculty)
        
        return format_success_response(
            formatted_faculty,
            "Faculty updated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error updating faculty: {e}")
        return format_error_response(e, "Failed to update faculty")


async def delete_faculty(faculty_id: str) -> Dict[str, Any]:
    """
    Delete faculty member record.
    
    Args:
        faculty_id: Faculty ObjectId
    """
    try:
        # Validate faculty ID
        if not validate_object_id(faculty_id):
            return format_error_response(
                ValueError("Invalid faculty ID format"),
                "Invalid faculty ID format"
            )
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Check if faculty exists
        faculty = await db_ops.find_one("faculties", {"_id": faculty_id})
        if not faculty:
            return format_error_response(
                ValueError("Faculty not found"),
                "Faculty not found"
            )
        
        # Delete faculty
        success = await db_ops.delete_one("faculties", {"_id": faculty_id})
        
        if not success:
            return format_error_response(
                ValueError("Delete failed"),
                "Failed to delete faculty"
            )
        
        return format_success_response(
            {"deleted_faculty": format_faculty_data(faculty)},
            f"Faculty {faculty.get('employeeId')} deleted successfully"
        )
        
    except Exception as e:
        logger.error(f"Error deleting faculty: {e}")
        return format_error_response(e, "Failed to delete faculty")


async def search_faculties(
    query: str,
    page: int = 1,
    page_size: int = 50,
    search_fields: List[str] = None
) -> Dict[str, Any]:
    """
    Search faculty members by multiple criteria.
    
    Args:
        query: Search query string
        page: Page number (default: 1)
        page_size: Number of items per page (default: 50)
        search_fields: Fields to search in (default: all text fields)
    """
    try:
        # Validate search query
        if not validate_search_query(query):
            return format_error_response(
                ValueError("Invalid search query"),
                "Search query must be between 1 and 100 characters"
            )
        
        # Validate pagination parameters
        page, page_size = validate_pagination_params(page, page_size)
        
        # Default search fields
        if search_fields is None:
            search_fields = ["employeeId", "fullName", "email", "designation", "subjects"]
        
        # Build MongoDB text search query
        search_query = {
            "$or": [
                {field: {"$regex": query, "$options": "i"}}
                for field in search_fields
            ]
        }
        
        # Calculate skip
        skip = (page - 1) * page_size
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Search faculties
        faculties = await db_ops.find_many(
            "faculties",
            query=search_query,
            skip=skip,
            limit=page_size,
            sort=[("fullName", 1)]
        )
        
        # Get total count
        total_count = await db_ops.count_documents("faculties", search_query)
        
        # Format faculties data
        formatted_faculties = [format_faculty_data(faculty) for faculty in faculties]
        
        return format_paginated_response(
            formatted_faculties,
            page,
            page_size,
            total_count,
            f"Found {len(formatted_faculties)} faculty members matching '{query}'"
        )
        
    except Exception as e:
        logger.error(f"Error searching faculties: {e}")
        return format_error_response(e, "Failed to search faculties")


async def assign_subjects_to_faculty(
    faculty_id: str,
    subjects: List[str]
) -> Dict[str, Any]:
    """
    Assign subjects to a faculty member.
    
    Args:
        faculty_id: Faculty ObjectId
        subjects: List of subjects to assign
    """
    try:
        # Validate faculty ID
        if not validate_object_id(faculty_id):
            return format_error_response(
                ValueError("Invalid faculty ID format"),
                "Invalid faculty ID format"
            )
        
        if not subjects or not isinstance(subjects, list):
            return format_error_response(
                ValueError("Invalid subjects"),
                "Subjects must be a non-empty list"
            )
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Check if faculty exists
        faculty = await db_ops.find_one("faculties", {"_id": faculty_id})
        if not faculty:
            return format_error_response(
                ValueError("Faculty not found"),
                "Faculty not found"
            )
        
        # Update faculty with new subjects
        success = await db_ops.update_one(
            "faculties",
            {"_id": faculty_id},
            {
                "$set": {
                    "subjects": subjects,
                    "updatedAt": datetime.now()
                }
            }
        )
        
        if not success:
            return format_error_response(
                ValueError("Update failed"),
                "Failed to assign subjects to faculty"
            )
        
        # Get updated faculty
        updated_faculty = await db_ops.find_one("faculties", {"_id": faculty_id})
        formatted_faculty = format_faculty_data(updated_faculty)
        
        return format_success_response(
            formatted_faculty,
            f"Assigned {len(subjects)} subjects to faculty successfully"
        )
        
    except Exception as e:
        logger.error(f"Error assigning subjects to faculty: {e}")
        return format_error_response(e, "Failed to assign subjects to faculty")


async def get_faculty_workload(faculty_id: str) -> Dict[str, Any]:
    """
    Calculate teaching workload for a faculty member.
    
    Args:
        faculty_id: Faculty ObjectId
    """
    try:
        # Validate faculty ID
        if not validate_object_id(faculty_id):
            return format_error_response(
                ValueError("Invalid faculty ID format"),
                "Invalid faculty ID format"
            )
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Check if faculty exists
        faculty = await db_ops.find_one("faculties", {"_id": faculty_id})
        if not faculty:
            return format_error_response(
                ValueError("Faculty not found"),
                "Faculty not found"
            )
        
        # Get courses assigned to this faculty
        courses = await db_ops.find_many("courses", {"facultyInCharge": faculty_id})
        
        # Calculate workload statistics
        total_courses = len(courses)
        total_credits = sum(course.get("credits", 0) for course in courses)
        subjects_taught = len(faculty.get("subjects", []))
        
        # Get timetable slots for this faculty
        timetable_slots = await db_ops.aggregate("timetables", [
            {"$match": {"slots.type": "class"}},
            {"$unwind": "$slots"},
            {"$match": {"slots.facultyId": faculty_id}},
            {"$count": "total_slots"}
        ])
        
        total_slots = timetable_slots[0].get("total_slots", 0) if timetable_slots else 0
        
        workload_data = {
            "faculty": format_faculty_data(faculty),
            "workload": {
                "total_courses": total_courses,
                "total_credits": total_credits,
                "subjects_taught": subjects_taught,
                "total_timetable_slots": total_slots,
                "courses": [format_course_data(course) for course in courses]
            }
        }
        
        return format_success_response(
            workload_data,
            f"Workload calculated for faculty {faculty.get('employeeId')}"
        )
        
    except Exception as e:
        logger.error(f"Error calculating faculty workload: {e}")
        return format_error_response(e, "Failed to calculate faculty workload")


def format_course_data(course: Dict[str, Any]) -> Dict[str, Any]:
    """Format course data for response."""
    if not course:
        return {}
    
    return {
        "id": str(course.get("_id")),
        "code": course.get("code"),
        "title": course.get("title"),
        "credits": course.get("credits"),
        "semester": course.get("semester")
    }


# MCP Tool definitions
def get_faculty_tools() -> List[Tool]:
    """Get all faculty management tools."""
    return [
        Tool(
            name="get_faculties",
            description="Get list of faculty members with optional filtering and pagination",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "default": 1, "description": "Page number"},
                    "page_size": {"type": "integer", "default": 50, "description": "Number of items per page"},
                    "designation": {"type": "string", "description": "Filter by designation"},
                    "sort_by": {"type": "string", "default": "fullName", "description": "Field to sort by"},
                    "sort_order": {"type": "string", "enum": ["asc", "desc"], "default": "asc", "description": "Sort order"}
                }
            }
        ),
        Tool(
            name="get_faculty_by_id",
            description="Get specific faculty member by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "faculty_id": {"type": "string", "description": "Faculty ObjectId"}
                },
                "required": ["faculty_id"]
            }
        ),
        Tool(
            name="create_faculty",
            description="Create new faculty member record",
            inputSchema={
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string", "description": "Faculty employee ID (e.g., EMP001)"},
                    "full_name": {"type": "string", "description": "Faculty full name"},
                    "email": {"type": "string", "description": "Faculty email address"},
                    "designation": {"type": "string", "description": "Faculty designation/position"},
                    "phone": {"type": "string", "description": "Faculty phone number (optional)"},
                    "subjects": {"type": "array", "items": {"type": "string"}, "description": "List of subjects taught (optional)"}
                },
                "required": ["employee_id", "full_name", "email", "designation"]
            }
        ),
        Tool(
            name="update_faculty",
            description="Update existing faculty member record",
            inputSchema={
                "type": "object",
                "properties": {
                    "faculty_id": {"type": "string", "description": "Faculty ObjectId"},
                    "employee_id": {"type": "string", "description": "Updated employee ID (optional)"},
                    "full_name": {"type": "string", "description": "Updated full name (optional)"},
                    "email": {"type": "string", "description": "Updated email (optional)"},
                    "designation": {"type": "string", "description": "Updated designation (optional)"},
                    "phone": {"type": "string", "description": "Updated phone (optional)"},
                    "subjects": {"type": "array", "items": {"type": "string"}, "description": "Updated subjects list (optional)"}
                },
                "required": ["faculty_id"]
            }
        ),
        Tool(
            name="delete_faculty",
            description="Delete faculty member record",
            inputSchema={
                "type": "object",
                "properties": {
                    "faculty_id": {"type": "string", "description": "Faculty ObjectId"}
                },
                "required": ["faculty_id"]
            }
        ),
        Tool(
            name="search_faculties",
            description="Search faculty members by multiple criteria",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query string"},
                    "page": {"type": "integer", "default": 1, "description": "Page number"},
                    "page_size": {"type": "integer", "default": 50, "description": "Number of items per page"},
                    "search_fields": {"type": "array", "items": {"type": "string"}, "description": "Fields to search in"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="assign_subjects_to_faculty",
            description="Assign subjects to a faculty member",
            inputSchema={
                "type": "object",
                "properties": {
                    "faculty_id": {"type": "string", "description": "Faculty ObjectId"},
                    "subjects": {"type": "array", "items": {"type": "string"}, "description": "List of subjects to assign"}
                },
                "required": ["faculty_id", "subjects"]
            }
        ),
        Tool(
            name="get_faculty_workload",
            description="Calculate teaching workload for a faculty member",
            inputSchema={
                "type": "object",
                "properties": {
                    "faculty_id": {"type": "string", "description": "Faculty ObjectId"}
                },
                "required": ["faculty_id"]
            }
        )
    ]
