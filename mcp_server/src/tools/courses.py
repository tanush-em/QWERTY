"""
Course management tools for CSE-AIML ERP MCP Server.
"""
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from mcp.server.models import Tool
from pymongo.errors import DuplicateKeyError

from ..database import get_db_operations
from ..utils.validators import (
    validate_course_data, validate_object_id, validate_pagination_params,
    validate_search_query, validate_course_code, validate_credits, validate_semester
)
from ..utils.formatters import (
    format_course_data, format_success_response, format_error_response,
    format_paginated_response
)

logger = logging.getLogger(__name__)


async def get_courses(
    page: int = 1,
    page_size: int = 50,
    semester: Optional[int] = None,
    sort_by: str = "code",
    sort_order: str = "asc"
) -> Dict[str, Any]:
    """
    Get list of courses with optional filtering and pagination.
    
    Args:
        page: Page number (default: 1)
        page_size: Number of items per page (default: 50)
        semester: Filter by semester
        sort_by: Field to sort by (default: code)
        sort_order: Sort order - asc or desc (default: asc)
    """
    try:
        # Validate pagination parameters
        page, page_size = validate_pagination_params(page, page_size)
        
        # Build query
        query = {}
        if semester is not None:
            query["semester"] = semester
        
        # Build sort
        sort_direction = 1 if sort_order.lower() == "asc" else -1
        sort = [(sort_by, sort_direction)]
        
        # Calculate skip
        skip = (page - 1) * page_size
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get courses
        courses = await db_ops.find_many(
            "courses",
            query=query,
            skip=skip,
            limit=page_size,
            sort=sort
        )
        
        # Get total count
        total_count = await db_ops.count_documents("courses", query)
        
        # Format courses data
        formatted_courses = [format_course_data(course) for course in courses]
        
        return format_paginated_response(
            formatted_courses,
            page,
            page_size,
            total_count,
            f"Retrieved {len(formatted_courses)} courses"
        )
        
    except Exception as e:
        logger.error(f"Error getting courses: {e}")
        return format_error_response(e, "Failed to retrieve courses")


async def get_course_by_id(course_id: str) -> Dict[str, Any]:
    """
    Get specific course by ID.
    
    Args:
        course_id: Course ObjectId
    """
    try:
        # Validate course ID
        if not validate_object_id(course_id):
            return format_error_response(
                ValueError("Invalid course ID format"),
                "Invalid course ID format"
            )
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get course
        course = await db_ops.find_one("courses", {"_id": course_id})
        
        if not course:
            return format_error_response(
                ValueError("Course not found"),
                "Course not found"
            )
        
        # Format course data
        formatted_course = format_course_data(course)
        
        return format_success_response(
            formatted_course,
            "Course retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting course by ID: {e}")
        return format_error_response(e, "Failed to retrieve course")


async def create_course(
    code: str,
    title: str,
    credits: float,
    semester: int,
    description: Optional[str] = None,
    faculty_in_charge: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create new course record.
    
    Args:
        code: Course code (e.g., CS101)
        title: Course title
        credits: Number of credits (1-6)
        semester: Semester number (1-8)
        description: Course description (optional)
        faculty_in_charge: Faculty ObjectId in charge (optional)
    """
    try:
        # Prepare course data
        course_data = {
            "code": code,
            "title": title,
            "credits": credits,
            "semester": semester,
            "description": description,
            "facultyInCharge": faculty_in_charge,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        # Validate course data
        validation_errors = validate_course_data(course_data)
        if validation_errors:
            return format_error_response(
                ValueError("Validation failed"),
                "Validation failed",
                errors=[str(error) for error_list in validation_errors.values() for error in error_list]
            )
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Check if course with same code already exists
        existing_course = await db_ops.find_one("courses", {"code": code})
        if existing_course:
            return format_error_response(
                ValueError("Course already exists"),
                f"Course with code {code} already exists"
            )
        
        # Create course
        course_id = await db_ops.insert_one("courses", course_data)
        
        # Get created course
        created_course = await db_ops.find_one("courses", {"_id": course_id})
        formatted_course = format_course_data(created_course)
        
        return format_success_response(
            formatted_course,
            f"Course {code} created successfully"
        )
        
    except DuplicateKeyError as e:
        logger.error(f"Duplicate key error creating course: {e}")
        return format_error_response(e, "Course with this code already exists")
    except Exception as e:
        logger.error(f"Error creating course: {e}")
        return format_error_response(e, "Failed to create course")


async def update_course(
    course_id: str,
    code: Optional[str] = None,
    title: Optional[str] = None,
    credits: Optional[float] = None,
    semester: Optional[int] = None,
    description: Optional[str] = None,
    faculty_in_charge: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update existing course record.
    
    Args:
        course_id: Course ObjectId
        code: Updated course code (optional)
        title: Updated title (optional)
        credits: Updated credits (optional)
        semester: Updated semester (optional)
        description: Updated description (optional)
        faculty_in_charge: Updated faculty in charge (optional)
    """
    try:
        # Validate course ID
        if not validate_object_id(course_id):
            return format_error_response(
                ValueError("Invalid course ID format"),
                "Invalid course ID format"
            )
        
        # Prepare update data
        update_data = {}
        if code is not None:
            update_data["code"] = code
        if title is not None:
            update_data["title"] = title
        if credits is not None:
            update_data["credits"] = credits
        if semester is not None:
            update_data["semester"] = semester
        if description is not None:
            update_data["description"] = description
        if faculty_in_charge is not None:
            update_data["facultyInCharge"] = faculty_in_charge
        
        if not update_data:
            return format_error_response(
                ValueError("No update data provided"),
                "No update data provided"
            )
        
        update_data["updatedAt"] = datetime.now()
        
        # Validate updated data if critical fields are being updated
        if code or credits or semester:
            # Get existing course to merge with updates
            db_ops = await get_db_operations()
            existing_course = await db_ops.find_one("courses", {"_id": course_id})
            
            if not existing_course:
                return format_error_response(
                    ValueError("Course not found"),
                    "Course not found"
                )
            
            # Merge existing data with updates
            merged_data = {**existing_course, **update_data}
            validation_errors = validate_course_data(merged_data)
            if validation_errors:
                return format_error_response(
                    ValueError("Validation failed"),
                    "Validation failed",
                    errors=[str(error) for error_list in validation_errors.values() for error in error_list]
                )
        
        # Update course
        success = await db_ops.update_one(
            "courses",
            {"_id": course_id},
            {"$set": update_data}
        )
        
        if not success:
            return format_error_response(
                ValueError("Update failed"),
                "No changes made to course record"
            )
        
        # Get updated course
        updated_course = await db_ops.find_one("courses", {"_id": course_id})
        formatted_course = format_course_data(updated_course)
        
        return format_success_response(
            formatted_course,
            "Course updated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error updating course: {e}")
        return format_error_response(e, "Failed to update course")


async def delete_course(course_id: str) -> Dict[str, Any]:
    """
    Delete course record.
    
    Args:
        course_id: Course ObjectId
    """
    try:
        # Validate course ID
        if not validate_object_id(course_id):
            return format_error_response(
                ValueError("Invalid course ID format"),
                "Invalid course ID format"
            )
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Check if course exists
        course = await db_ops.find_one("courses", {"_id": course_id})
        if not course:
            return format_error_response(
                ValueError("Course not found"),
                "Course not found"
            )
        
        # Delete course
        success = await db_ops.delete_one("courses", {"_id": course_id})
        
        if not success:
            return format_error_response(
                ValueError("Delete failed"),
                "Failed to delete course"
            )
        
        return format_success_response(
            {"deleted_course": format_course_data(course)},
            f"Course {course.get('code')} deleted successfully"
        )
        
    except Exception as e:
        logger.error(f"Error deleting course: {e}")
        return format_error_response(e, "Failed to delete course")


async def search_courses(
    query: str,
    page: int = 1,
    page_size: int = 50,
    search_fields: List[str] = None
) -> Dict[str, Any]:
    """
    Search courses by multiple criteria.
    
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
            search_fields = ["code", "title", "description"]
        
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
        
        # Search courses
        courses = await db_ops.find_many(
            "courses",
            query=search_query,
            skip=skip,
            limit=page_size,
            sort=[("code", 1)]
        )
        
        # Get total count
        total_count = await db_ops.count_documents("courses", search_query)
        
        # Format courses data
        formatted_courses = [format_course_data(course) for course in courses]
        
        return format_paginated_response(
            formatted_courses,
            page,
            page_size,
            total_count,
            f"Found {len(formatted_courses)} courses matching '{query}'"
        )
        
    except Exception as e:
        logger.error(f"Error searching courses: {e}")
        return format_error_response(e, "Failed to search courses")


async def assign_faculty_to_course(
    course_id: str,
    faculty_id: str
) -> Dict[str, Any]:
    """
    Assign faculty member to a course.
    
    Args:
        course_id: Course ObjectId
        faculty_id: Faculty ObjectId
    """
    try:
        # Validate IDs
        if not validate_object_id(course_id):
            return format_error_response(
                ValueError("Invalid course ID format"),
                "Invalid course ID format"
            )
        
        if not validate_object_id(faculty_id):
            return format_error_response(
                ValueError("Invalid faculty ID format"),
                "Invalid faculty ID format"
            )
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Check if course exists
        course = await db_ops.find_one("courses", {"_id": course_id})
        if not course:
            return format_error_response(
                ValueError("Course not found"),
                "Course not found"
            )
        
        # Check if faculty exists
        faculty = await db_ops.find_one("faculties", {"_id": faculty_id})
        if not faculty:
            return format_error_response(
                ValueError("Faculty not found"),
                "Faculty not found"
            )
        
        # Update course with faculty assignment
        success = await db_ops.update_one(
            "courses",
            {"_id": course_id},
            {
                "$set": {
                    "facultyInCharge": faculty_id,
                    "updatedAt": datetime.now()
                }
            }
        )
        
        if not success:
            return format_error_response(
                ValueError("Update failed"),
                "Failed to assign faculty to course"
            )
        
        # Get updated course
        updated_course = await db_ops.find_one("courses", {"_id": course_id})
        formatted_course = format_course_data(updated_course)
        
        return format_success_response(
            formatted_course,
            f"Faculty {faculty.get('employeeId')} assigned to course {course.get('code')}"
        )
        
    except Exception as e:
        logger.error(f"Error assigning faculty to course: {e}")
        return format_error_response(e, "Failed to assign faculty to course")


async def get_courses_by_semester(
    semester: int,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """
    Get courses filtered by semester.
    
    Args:
        semester: Semester number (1-8)
        page: Page number (default: 1)
        page_size: Number of items per page (default: 50)
    """
    try:
        # Validate semester
        if not validate_semester(semester):
            return format_error_response(
                ValueError("Invalid semester"),
                "Semester must be between 1 and 8"
            )
        
        # Validate pagination parameters
        page, page_size = validate_pagination_params(page, page_size)
        
        # Calculate skip
        skip = (page - 1) * page_size
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get courses by semester
        courses = await db_ops.find_many(
            "courses",
            query={"semester": semester},
            skip=skip,
            limit=page_size,
            sort=[("code", 1)]
        )
        
        # Get total count
        total_count = await db_ops.count_documents("courses", {"semester": semester})
        
        # Format courses data
        formatted_courses = [format_course_data(course) for course in courses]
        
        return format_paginated_response(
            formatted_courses,
            page,
            page_size,
            total_count,
            f"Retrieved {len(formatted_courses)} courses for semester {semester}"
        )
        
    except Exception as e:
        logger.error(f"Error getting courses by semester: {e}")
        return format_error_response(e, "Failed to retrieve courses by semester")


async def get_course_statistics() -> Dict[str, Any]:
    """
    Get course statistics and analytics.
    """
    try:
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get total courses count
        total_courses = await db_ops.count_documents("courses", {})
        
        # Get courses by semester
        semester_stats = await db_ops.aggregate("courses", [
            {"$group": {"_id": "$semester", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ])
        
        # Get total credits
        credits_stats = await db_ops.aggregate("courses", [
            {"$group": {"_id": None, "total_credits": {"$sum": "$credits"}, "avg_credits": {"$avg": "$credits"}}}
        ])
        
        # Get courses with faculty assigned
        courses_with_faculty = await db_ops.count_documents("courses", {"facultyInCharge": {"$exists": True, "$ne": None}})
        
        # Get courses without faculty assigned
        courses_without_faculty = total_courses - courses_with_faculty
        
        statistics = {
            "total_courses": total_courses,
            "courses_with_faculty": courses_with_faculty,
            "courses_without_faculty": courses_without_faculty,
            "semester_distribution": {str(stat["_id"]): stat["count"] for stat in semester_stats},
            "credits_summary": {
                "total_credits": credits_stats[0].get("total_credits", 0) if credits_stats else 0,
                "average_credits": round(credits_stats[0].get("avg_credits", 0), 2) if credits_stats else 0
            }
        }
        
        return format_success_response(
            statistics,
            "Course statistics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting course statistics: {e}")
        return format_error_response(e, "Failed to retrieve course statistics")


# MCP Tool definitions
def get_course_tools() -> List[Tool]:
    """Get all course management tools."""
    return [
        Tool(
            name="get_courses",
            description="Get list of courses with optional filtering and pagination",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "default": 1, "description": "Page number"},
                    "page_size": {"type": "integer", "default": 50, "description": "Number of items per page"},
                    "semester": {"type": "integer", "description": "Filter by semester"},
                    "sort_by": {"type": "string", "default": "code", "description": "Field to sort by"},
                    "sort_order": {"type": "string", "enum": ["asc", "desc"], "default": "asc", "description": "Sort order"}
                }
            }
        ),
        Tool(
            name="get_course_by_id",
            description="Get specific course by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_id": {"type": "string", "description": "Course ObjectId"}
                },
                "required": ["course_id"]
            }
        ),
        Tool(
            name="create_course",
            description="Create new course record",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Course code (e.g., CS101)"},
                    "title": {"type": "string", "description": "Course title"},
                    "credits": {"type": "number", "description": "Number of credits (1-6)"},
                    "semester": {"type": "integer", "description": "Semester number (1-8)"},
                    "description": {"type": "string", "description": "Course description (optional)"},
                    "faculty_in_charge": {"type": "string", "description": "Faculty ObjectId in charge (optional)"}
                },
                "required": ["code", "title", "credits", "semester"]
            }
        ),
        Tool(
            name="update_course",
            description="Update existing course record",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_id": {"type": "string", "description": "Course ObjectId"},
                    "code": {"type": "string", "description": "Updated course code (optional)"},
                    "title": {"type": "string", "description": "Updated title (optional)"},
                    "credits": {"type": "number", "description": "Updated credits (optional)"},
                    "semester": {"type": "integer", "description": "Updated semester (optional)"},
                    "description": {"type": "string", "description": "Updated description (optional)"},
                    "faculty_in_charge": {"type": "string", "description": "Updated faculty in charge (optional)"}
                },
                "required": ["course_id"]
            }
        ),
        Tool(
            name="delete_course",
            description="Delete course record",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_id": {"type": "string", "description": "Course ObjectId"}
                },
                "required": ["course_id"]
            }
        ),
        Tool(
            name="search_courses",
            description="Search courses by multiple criteria",
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
            name="assign_faculty_to_course",
            description="Assign faculty member to a course",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_id": {"type": "string", "description": "Course ObjectId"},
                    "faculty_id": {"type": "string", "description": "Faculty ObjectId"}
                },
                "required": ["course_id", "faculty_id"]
            }
        ),
        Tool(
            name="get_courses_by_semester",
            description="Get courses filtered by semester",
            inputSchema={
                "type": "object",
                "properties": {
                    "semester": {"type": "integer", "description": "Semester number (1-8)"},
                    "page": {"type": "integer", "default": 1, "description": "Page number"},
                    "page_size": {"type": "integer", "default": 50, "description": "Number of items per page"}
                },
                "required": ["semester"]
            }
        ),
        Tool(
            name="get_course_statistics",
            description="Get course statistics and analytics",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]
