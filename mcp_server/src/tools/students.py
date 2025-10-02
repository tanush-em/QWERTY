"""
Student management tools for CSE-AIML ERP MCP Server.
"""
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from mcp import Tool
from mcp.server import Server
from pymongo.errors import DuplicateKeyError

from database import get_db_operations
from utils.validators import (
    validate_student_data, validate_object_id, validate_pagination_params,
    validate_search_query, validate_roll_number
)
from utils.formatters import (
    format_student_data, format_success_response, format_error_response,
    format_paginated_response
)

logger = logging.getLogger(__name__)


async def get_students(
    page: int = 1,
    page_size: int = 50,
    year: Optional[str] = None,
    batch: Optional[str] = None,
    sort_by: str = "roll",
    sort_order: str = "asc"
) -> Dict[str, Any]:
    """
    Get list of students with optional filtering and pagination.
    
    Args:
        page: Page number (default: 1)
        page_size: Number of items per page (default: 50)
        year: Filter by academic year
        batch: Filter by batch
        sort_by: Field to sort by (default: roll)
        sort_order: Sort order - asc or desc (default: asc)
    """
    try:
        # Validate pagination parameters
        page, page_size = validate_pagination_params(page, page_size)
        
        # Build query
        query = {}
        if year:
            query["year"] = year
        if batch:
            query["batch"] = batch
        
        # Build sort
        sort_direction = 1 if sort_order.lower() == "asc" else -1
        sort = [(sort_by, sort_direction)]
        
        # Calculate skip
        skip = (page - 1) * page_size
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get students
        students = await db_ops.find_many(
            "students",
            query=query,
            skip=skip,
            limit=page_size,
            sort=sort
        )
        
        # Get total count
        total_count = await db_ops.count_documents("students", query)
        
        # Format students data
        formatted_students = [format_student_data(student) for student in students]
        
        return format_paginated_response(
            formatted_students,
            page,
            page_size,
            total_count,
            f"Retrieved {len(formatted_students)} students"
        )
        
    except Exception as e:
        logger.error(f"Error getting students: {e}")
        return format_error_response(e, "Failed to retrieve students")


async def get_student_by_id(student_id: str) -> Dict[str, Any]:
    """
    Get specific student by ID.
    
    Args:
        student_id: Student ObjectId
    """
    try:
        # Validate student ID
        if not validate_object_id(student_id):
            return format_error_response(
                ValueError("Invalid student ID format"),
                "Invalid student ID format"
            )
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get student
        student = await db_ops.find_one("students", {"_id": student_id})
        
        if not student:
            return format_error_response(
                ValueError("Student not found"),
                "Student not found"
            )
        
        # Format student data
        formatted_student = format_student_data(student)
        
        return format_success_response(
            formatted_student,
            "Student retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting student by ID: {e}")
        return format_error_response(e, "Failed to retrieve student")


async def create_student(
    roll: str,
    full_name: str,
    email: str,
    phone: Optional[str] = None,
    year: Optional[str] = None,
    batch: Optional[str] = None,
    date_of_birth: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create new student record.
    
    Args:
        roll: Student roll number (e.g., CSE001)
        full_name: Student full name
        email: Student email address
        phone: Student phone number (optional)
        year: Academic year (optional)
        batch: Batch identifier (optional)
        date_of_birth: Date of birth in ISO format (optional)
    """
    try:
        # Prepare student data
        student_data = {
            "roll": roll,
            "fullName": full_name,
            "email": email,
            "phone": phone,
            "year": year,
            "batch": batch,
            "dateOfBirth": date_of_birth,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        # Validate student data
        validation_errors = validate_student_data(student_data)
        if validation_errors:
            return format_error_response(
                ValueError("Validation failed"),
                "Validation failed"
            )
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Check if student with same roll already exists
        existing_student = await db_ops.find_one("students", {"roll": roll})
        if existing_student:
            return format_error_response(
                ValueError("Student already exists"),
                f"Student with roll number {roll} already exists"
            )
        
        # Create student
        student_id = await db_ops.insert_one("students", student_data)
        
        # Get created student
        created_student = await db_ops.find_one("students", {"_id": student_id})
        formatted_student = format_student_data(created_student)
        
        return format_success_response(
            formatted_student,
            f"Student {roll} created successfully"
        )
        
    except DuplicateKeyError as e:
        logger.error(f"Duplicate key error creating student: {e}")
        return format_error_response(e, "Student with this roll number already exists")
    except Exception as e:
        logger.error(f"Error creating student: {e}")
        return format_error_response(e, "Failed to create student")


async def update_student(
    student_id: str,
    roll: Optional[str] = None,
    full_name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    year: Optional[str] = None,
    batch: Optional[str] = None,
    date_of_birth: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update existing student record.
    
    Args:
        student_id: Student ObjectId
        roll: Updated roll number (optional)
        full_name: Updated full name (optional)
        email: Updated email (optional)
        phone: Updated phone (optional)
        year: Updated academic year (optional)
        batch: Updated batch (optional)
        date_of_birth: Updated date of birth (optional)
    """
    try:
        # Validate student ID
        if not validate_object_id(student_id):
            return format_error_response(
                ValueError("Invalid student ID format"),
                "Invalid student ID format"
            )
        
        # Prepare update data
        update_data = {}
        if roll is not None:
            update_data["roll"] = roll
        if full_name is not None:
            update_data["fullName"] = full_name
        if email is not None:
            update_data["email"] = email
        if phone is not None:
            update_data["phone"] = phone
        if year is not None:
            update_data["year"] = year
        if batch is not None:
            update_data["batch"] = batch
        if date_of_birth is not None:
            update_data["dateOfBirth"] = date_of_birth
        
        if not update_data:
            return format_error_response(
                ValueError("No update data provided"),
                "No update data provided"
            )
        
        update_data["updatedAt"] = datetime.now()
        
        # Validate updated data if roll or email is being updated
        if roll or email:
            # Get existing student to merge with updates
            db_ops = await get_db_operations()
            existing_student = await db_ops.find_one("students", {"_id": student_id})
            
            if not existing_student:
                return format_error_response(
                    ValueError("Student not found"),
                    "Student not found"
                )
            
            # Merge existing data with updates
            merged_data = {**existing_student, **update_data}
            validation_errors = validate_student_data(merged_data)
            if validation_errors:
                return format_error_response(
                    ValueError("Validation failed"),
                    "Validation failed"
                )
        
        # Update student
        success = await db_ops.update_one(
            "students",
            {"_id": student_id},
            {"$set": update_data}
        )
        
        if not success:
            return format_error_response(
                ValueError("Update failed"),
                "No changes made to student record"
            )
        
        # Get updated student
        updated_student = await db_ops.find_one("students", {"_id": student_id})
        formatted_student = format_student_data(updated_student)
        
        return format_success_response(
            formatted_student,
            "Student updated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error updating student: {e}")
        return format_error_response(e, "Failed to update student")


async def delete_student(student_id: str) -> Dict[str, Any]:
    """
    Delete student record.
    
    Args:
        student_id: Student ObjectId
    """
    try:
        # Validate student ID
        if not validate_object_id(student_id):
            return format_error_response(
                ValueError("Invalid student ID format"),
                "Invalid student ID format"
            )
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Check if student exists
        student = await db_ops.find_one("students", {"_id": student_id})
        if not student:
            return format_error_response(
                ValueError("Student not found"),
                "Student not found"
            )
        
        # Delete student
        success = await db_ops.delete_one("students", {"_id": student_id})
        
        if not success:
            return format_error_response(
                ValueError("Delete failed"),
                "Failed to delete student"
            )
        
        return format_success_response(
            {"deleted_student": format_student_data(student)},
            f"Student {student.get('roll')} deleted successfully"
        )
        
    except Exception as e:
        logger.error(f"Error deleting student: {e}")
        return format_error_response(e, "Failed to delete student")


async def search_students(
    query: str,
    page: int = 1,
    page_size: int = 50,
    search_fields: List[str] = None
) -> Dict[str, Any]:
    """
    Search students by multiple criteria.
    
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
            search_fields = ["roll", "fullName", "email", "year", "batch"]
        
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
        
        # Search students
        students = await db_ops.find_many(
            "students",
            query=search_query,
            skip=skip,
            limit=page_size,
            sort=[("roll", 1)]
        )
        
        # Get total count
        total_count = await db_ops.count_documents("students", search_query)
        
        # Format students data
        formatted_students = [format_student_data(student) for student in students]
        
        return format_paginated_response(
            formatted_students,
            page,
            page_size,
            total_count,
            f"Found {len(formatted_students)} students matching '{query}'"
        )
        
    except Exception as e:
        logger.error(f"Error searching students: {e}")
        return format_error_response(e, "Failed to search students")


async def get_students_by_year(year: str, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
    """
    Get students filtered by academic year.
    
    Args:
        year: Academic year (e.g., "2024", "2024-25")
        page: Page number (default: 1)
        page_size: Number of items per page (default: 50)
    """
    try:
        # Validate pagination parameters
        page, page_size = validate_pagination_params(page, page_size)
        
        # Calculate skip
        skip = (page - 1) * page_size
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get students by year
        students = await db_ops.find_many(
            "students",
            query={"year": year},
            skip=skip,
            limit=page_size,
            sort=[("roll", 1)]
        )
        
        # Get total count
        total_count = await db_ops.count_documents("students", {"year": year})
        
        # Format students data
        formatted_students = [format_student_data(student) for student in students]
        
        return format_paginated_response(
            formatted_students,
            page,
            page_size,
            total_count,
            f"Retrieved {len(formatted_students)} students for year {year}"
        )
        
    except Exception as e:
        logger.error(f"Error getting students by year: {e}")
        return format_error_response(e, "Failed to retrieve students by year")


async def get_students_by_batch(batch: str, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
    """
    Get students filtered by batch.
    
    Args:
        batch: Batch identifier
        page: Page number (default: 1)
        page_size: Number of items per page (default: 50)
    """
    try:
        # Validate pagination parameters
        page, page_size = validate_pagination_params(page, page_size)
        
        # Calculate skip
        skip = (page - 1) * page_size
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get students by batch
        students = await db_ops.find_many(
            "students",
            query={"batch": batch},
            skip=skip,
            limit=page_size,
            sort=[("roll", 1)]
        )
        
        # Get total count
        total_count = await db_ops.count_documents("students", {"batch": batch})
        
        # Format students data
        formatted_students = [format_student_data(student) for student in students]
        
        return format_paginated_response(
            formatted_students,
            page,
            page_size,
            total_count,
            f"Retrieved {len(formatted_students)} students for batch {batch}"
        )
        
    except Exception as e:
        logger.error(f"Error getting students by batch: {e}")
        return format_error_response(e, "Failed to retrieve students by batch")


# MCP Tool definitions
def get_student_tools() -> List[Tool]:
    """Get all student management tools."""
    return [
        Tool(
            name="get_students",
            description="Get list of students with optional filtering and pagination",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "default": 1, "description": "Page number"},
                    "page_size": {"type": "integer", "default": 50, "description": "Number of items per page"},
                    "year": {"type": "string", "description": "Filter by academic year"},
                    "batch": {"type": "string", "description": "Filter by batch"},
                    "sort_by": {"type": "string", "default": "roll", "description": "Field to sort by"},
                    "sort_order": {"type": "string", "enum": ["asc", "desc"], "default": "asc", "description": "Sort order"}
                }
            }
        ),
        Tool(
            name="get_student_by_id",
            description="Get specific student by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {"type": "string", "description": "Student ObjectId"}
                },
                "required": ["student_id"]
            }
        ),
        Tool(
            name="create_student",
            description="Create new student record",
            inputSchema={
                "type": "object",
                "properties": {
                    "roll": {"type": "string", "description": "Student roll number (e.g., CSE001)"},
                    "full_name": {"type": "string", "description": "Student full name"},
                    "email": {"type": "string", "description": "Student email address"},
                    "phone": {"type": "string", "description": "Student phone number (optional)"},
                    "year": {"type": "string", "description": "Academic year (optional)"},
                    "batch": {"type": "string", "description": "Batch identifier (optional)"},
                    "date_of_birth": {"type": "string", "description": "Date of birth in ISO format (optional)"}
                },
                "required": ["roll", "full_name", "email"]
            }
        ),
        Tool(
            name="update_student",
            description="Update existing student record",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {"type": "string", "description": "Student ObjectId"},
                    "roll": {"type": "string", "description": "Updated roll number (optional)"},
                    "full_name": {"type": "string", "description": "Updated full name (optional)"},
                    "email": {"type": "string", "description": "Updated email (optional)"},
                    "phone": {"type": "string", "description": "Updated phone (optional)"},
                    "year": {"type": "string", "description": "Updated academic year (optional)"},
                    "batch": {"type": "string", "description": "Updated batch (optional)"},
                    "date_of_birth": {"type": "string", "description": "Updated date of birth (optional)"}
                },
                "required": ["student_id"]
            }
        ),
        Tool(
            name="delete_student",
            description="Delete student record",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {"type": "string", "description": "Student ObjectId"}
                },
                "required": ["student_id"]
            }
        ),
        Tool(
            name="search_students",
            description="Search students by multiple criteria",
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
            name="get_students_by_year",
            description="Get students filtered by academic year",
            inputSchema={
                "type": "object",
                "properties": {
                    "year": {"type": "string", "description": "Academic year (e.g., '2024', '2024-25')"},
                    "page": {"type": "integer", "default": 1, "description": "Page number"},
                    "page_size": {"type": "integer", "default": 50, "description": "Number of items per page"}
                },
                "required": ["year"]
            }
        ),
        Tool(
            name="get_students_by_batch",
            description="Get students filtered by batch",
            inputSchema={
                "type": "object",
                "properties": {
                    "batch": {"type": "string", "description": "Batch identifier"},
                    "page": {"type": "integer", "default": 1, "description": "Page number"},
                    "page_size": {"type": "integer", "default": 50, "description": "Number of items per page"}
                },
                "required": ["batch"]
            }
        )
    ]
