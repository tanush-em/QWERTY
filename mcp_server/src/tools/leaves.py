"""
Leave management tools for CSE-AIML ERP MCP Server.
"""
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, date
from mcp.server.models import Tool

from ..database import get_db_operations
from ..utils.validators import (
    validate_leave_data, validate_object_id, validate_pagination_params,
    validate_search_query, validate_leave_status, validate_date_range
)
from ..utils.formatters import (
    format_leave_data, format_success_response, format_error_response,
    format_paginated_response
)

logger = logging.getLogger(__name__)


async def get_leaves(
    page: int = 1,
    page_size: int = 50,
    status: Optional[str] = None,
    sort_by: str = "createdAt",
    sort_order: str = "desc"
) -> Dict[str, Any]:
    """
    Get list of leave applications with optional filtering and pagination.
    
    Args:
        page: Page number (default: 1)
        page_size: Number of items per page (default: 50)
        status: Filter by status (pending, approved, rejected, cancelled)
        sort_by: Field to sort by (default: createdAt)
        sort_order: Sort order - asc or desc (default: desc)
    """
    try:
        # Validate pagination parameters
        page, page_size = validate_pagination_params(page, page_size)
        
        # Build query
        query = {}
        if status and validate_leave_status(status):
            query["status"] = status.lower()
        
        # Build sort
        sort_direction = 1 if sort_order.lower() == "asc" else -1
        sort = [(sort_by, sort_direction)]
        
        # Calculate skip
        skip = (page - 1) * page_size
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get leaves
        leaves = await db_ops.find_many(
            "leaves",
            query=query,
            skip=skip,
            limit=page_size,
            sort=sort
        )
        
        # Get total count
        total_count = await db_ops.count_documents("leaves", query)
        
        # Format leaves data
        formatted_leaves = [format_leave_data(leave) for leave in leaves]
        
        return format_paginated_response(
            formatted_leaves,
            page,
            page_size,
            total_count,
            f"Retrieved {len(formatted_leaves)} leave applications"
        )
        
    except Exception as e:
        logger.error(f"Error getting leaves: {e}")
        return format_error_response(e, "Failed to retrieve leaves")


async def get_leave_by_id(leave_id: str) -> Dict[str, Any]:
    """
    Get specific leave application by ID.
    
    Args:
        leave_id: Leave ObjectId
    """
    try:
        # Validate leave ID
        if not validate_object_id(leave_id):
            return format_error_response(
                ValueError("Invalid leave ID format"),
                "Invalid leave ID format"
            )
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get leave
        leave = await db_ops.find_one("leaves", {"_id": leave_id})
        
        if not leave:
            return format_error_response(
                ValueError("Leave not found"),
                "Leave not found"
            )
        
        # Format leave data
        formatted_leave = format_leave_data(leave)
        
        return format_success_response(
            formatted_leave,
            "Leave retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting leave by ID: {e}")
        return format_error_response(e, "Failed to retrieve leave")


async def create_leave(
    student_id: str,
    start_date: str,
    end_date: str,
    reason: str,
    status: str = "pending"
) -> Dict[str, Any]:
    """
    Create new leave application.
    
    Args:
        student_id: Student ObjectId
        start_date: Start date in ISO format
        end_date: End date in ISO format
        reason: Leave reason
        status: Leave status (default: pending)
    """
    try:
        # Prepare leave data
        leave_data = {
            "studentId": student_id,
            "startDate": start_date,
            "endDate": end_date,
            "reason": reason,
            "status": status.lower(),
            "handledBy": None,
            "remarks": None,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        # Validate leave data
        validation_errors = validate_leave_data(leave_data)
        if validation_errors:
            return format_error_response(
                ValueError("Validation failed"),
                "Validation failed",
                errors=[str(error) for error_list in validation_errors.values() for error in error_list]
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
        
        # Create leave
        leave_id = await db_ops.insert_one("leaves", leave_data)
        
        # Get created leave
        created_leave = await db_ops.find_one("leaves", {"_id": leave_id})
        formatted_leave = format_leave_data(created_leave)
        
        return format_success_response(
            formatted_leave,
            f"Leave application created successfully for student {student.get('roll')}"
        )
        
    except Exception as e:
        logger.error(f"Error creating leave: {e}")
        return format_error_response(e, "Failed to create leave application")


async def update_leave(
    leave_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    reason: Optional[str] = None,
    status: Optional[str] = None,
    handled_by: Optional[str] = None,
    remarks: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update existing leave application.
    
    Args:
        leave_id: Leave ObjectId
        start_date: Updated start date (optional)
        end_date: Updated end date (optional)
        reason: Updated reason (optional)
        status: Updated status (optional)
        handled_by: Faculty ObjectId who handled (optional)
        remarks: Updated remarks (optional)
    """
    try:
        # Validate leave ID
        if not validate_object_id(leave_id):
            return format_error_response(
                ValueError("Invalid leave ID format"),
                "Invalid leave ID format"
            )
        
        # Prepare update data
        update_data = {}
        if start_date is not None:
            update_data["startDate"] = start_date
        if end_date is not None:
            update_data["endDate"] = end_date
        if reason is not None:
            update_data["reason"] = reason
        if status is not None:
            update_data["status"] = status.lower()
        if handled_by is not None:
            update_data["handledBy"] = handled_by
        if remarks is not None:
            update_data["remarks"] = remarks
        
        if not update_data:
            return format_error_response(
                ValueError("No update data provided"),
                "No update data provided"
            )
        
        update_data["updatedAt"] = datetime.now()
        
        # Validate updated data if dates or status are being updated
        if start_date or end_date or status:
            # Get existing leave to merge with updates
            db_ops = await get_db_operations()
            existing_leave = await db_ops.find_one("leaves", {"_id": leave_id})
            
            if not existing_leave:
                return format_error_response(
                    ValueError("Leave not found"),
                    "Leave not found"
                )
            
            # Merge existing data with updates
            merged_data = {**existing_leave, **update_data}
            validation_errors = validate_leave_data(merged_data)
            if validation_errors:
                return format_error_response(
                    ValueError("Validation failed"),
                    "Validation failed",
                    errors=[str(error) for error_list in validation_errors.values() for error in error_list]
                )
        
        # Update leave
        success = await db_ops.update_one(
            "leaves",
            {"_id": leave_id},
            {"$set": update_data}
        )
        
        if not success:
            return format_error_response(
                ValueError("Update failed"),
                "No changes made to leave record"
            )
        
        # Get updated leave
        updated_leave = await db_ops.find_one("leaves", {"_id": leave_id})
        formatted_leave = format_leave_data(updated_leave)
        
        return format_success_response(
            formatted_leave,
            "Leave updated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error updating leave: {e}")
        return format_error_response(e, "Failed to update leave")


async def delete_leave(leave_id: str) -> Dict[str, Any]:
    """
    Delete leave application.
    
    Args:
        leave_id: Leave ObjectId
    """
    try:
        # Validate leave ID
        if not validate_object_id(leave_id):
            return format_error_response(
                ValueError("Invalid leave ID format"),
                "Invalid leave ID format"
            )
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Check if leave exists
        leave = await db_ops.find_one("leaves", {"_id": leave_id})
        if not leave:
            return format_error_response(
                ValueError("Leave not found"),
                "Leave not found"
            )
        
        # Delete leave
        success = await db_ops.delete_one("leaves", {"_id": leave_id})
        
        if not success:
            return format_error_response(
                ValueError("Delete failed"),
                "Failed to delete leave"
            )
        
        return format_success_response(
            {"deleted_leave": format_leave_data(leave)},
            "Leave application deleted successfully"
        )
        
    except Exception as e:
        logger.error(f"Error deleting leave: {e}")
        return format_error_response(e, "Failed to delete leave")


async def approve_leave(
    leave_id: str,
    handled_by: str,
    remarks: Optional[str] = None
) -> Dict[str, Any]:
    """
    Approve leave application.
    
    Args:
        leave_id: Leave ObjectId
        handled_by: Faculty ObjectId who approved
        remarks: Optional remarks (optional)
    """
    try:
        # Validate IDs
        if not validate_object_id(leave_id):
            return format_error_response(
                ValueError("Invalid leave ID format"),
                "Invalid leave ID format"
            )
        
        if not validate_object_id(handled_by):
            return format_error_response(
                ValueError("Invalid faculty ID format"),
                "Invalid faculty ID format"
            )
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Check if leave exists
        leave = await db_ops.find_one("leaves", {"_id": leave_id})
        if not leave:
            return format_error_response(
                ValueError("Leave not found"),
                "Leave not found"
            )
        
        # Check if faculty exists
        faculty = await db_ops.find_one("faculties", {"_id": handled_by})
        if not faculty:
            return format_error_response(
                ValueError("Faculty not found"),
                "Faculty not found"
            )
        
        # Update leave status
        update_data = {
            "status": "approved",
            "handledBy": handled_by,
            "updatedAt": datetime.now()
        }
        
        if remarks:
            update_data["remarks"] = remarks
        
        success = await db_ops.update_one(
            "leaves",
            {"_id": leave_id},
            {"$set": update_data}
        )
        
        if not success:
            return format_error_response(
                ValueError("Update failed"),
                "Failed to approve leave"
            )
        
        # Get updated leave
        updated_leave = await db_ops.find_one("leaves", {"_id": leave_id})
        formatted_leave = format_leave_data(updated_leave)
        
        return format_success_response(
            formatted_leave,
            f"Leave approved by {faculty.get('employeeId')}"
        )
        
    except Exception as e:
        logger.error(f"Error approving leave: {e}")
        return format_error_response(e, "Failed to approve leave")


async def reject_leave(
    leave_id: str,
    handled_by: str,
    remarks: str
) -> Dict[str, Any]:
    """
    Reject leave application.
    
    Args:
        leave_id: Leave ObjectId
        handled_by: Faculty ObjectId who rejected
        remarks: Rejection reason (required)
    """
    try:
        # Validate IDs
        if not validate_object_id(leave_id):
            return format_error_response(
                ValueError("Invalid leave ID format"),
                "Invalid leave ID format"
            )
        
        if not validate_object_id(handled_by):
            return format_error_response(
                ValueError("Invalid faculty ID format"),
                "Invalid faculty ID format"
            )
        
        if not remarks or not remarks.strip():
            return format_error_response(
                ValueError("Remarks required"),
                "Remarks are required when rejecting a leave"
            )
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Check if leave exists
        leave = await db_ops.find_one("leaves", {"_id": leave_id})
        if not leave:
            return format_error_response(
                ValueError("Leave not found"),
                "Leave not found"
            )
        
        # Check if faculty exists
        faculty = await db_ops.find_one("faculties", {"_id": handled_by})
        if not faculty:
            return format_error_response(
                ValueError("Faculty not found"),
                "Faculty not found"
            )
        
        # Update leave status
        update_data = {
            "status": "rejected",
            "handledBy": handled_by,
            "remarks": remarks.strip(),
            "updatedAt": datetime.now()
        }
        
        success = await db_ops.update_one(
            "leaves",
            {"_id": leave_id},
            {"$set": update_data}
        )
        
        if not success:
            return format_error_response(
                ValueError("Update failed"),
                "Failed to reject leave"
            )
        
        # Get updated leave
        updated_leave = await db_ops.find_one("leaves", {"_id": leave_id})
        formatted_leave = format_leave_data(updated_leave)
        
        return format_success_response(
            formatted_leave,
            f"Leave rejected by {faculty.get('employeeId')}"
        )
        
    except Exception as e:
        logger.error(f"Error rejecting leave: {e}")
        return format_error_response(e, "Failed to reject leave")


async def get_leaves_by_student(
    student_id: str,
    page: int = 1,
    page_size: int = 50,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get leave applications for a specific student.
    
    Args:
        student_id: Student ObjectId
        page: Page number (default: 1)
        page_size: Number of items per page (default: 50)
        status: Filter by status (optional)
    """
    try:
        # Validate student ID
        if not validate_object_id(student_id):
            return format_error_response(
                ValueError("Invalid student ID format"),
                "Invalid student ID format"
            )
        
        # Validate pagination parameters
        page, page_size = validate_pagination_params(page, page_size)
        
        # Build query
        query = {"studentId": student_id}
        if status and validate_leave_status(status):
            query["status"] = status.lower()
        
        # Calculate skip
        skip = (page - 1) * page_size
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get leaves by student
        leaves = await db_ops.find_many(
            "leaves",
            query=query,
            skip=skip,
            limit=page_size,
            sort=[("createdAt", -1)]
        )
        
        # Get total count
        total_count = await db_ops.count_documents("leaves", query)
        
        # Format leaves data
        formatted_leaves = [format_leave_data(leave) for leave in leaves]
        
        return format_paginated_response(
            formatted_leaves,
            page,
            page_size,
            total_count,
            f"Retrieved {len(formatted_leaves)} leave applications for student"
        )
        
    except Exception as e:
        logger.error(f"Error getting leaves by student: {e}")
        return format_error_response(e, "Failed to retrieve leaves for student")


async def get_pending_leaves(
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """
    Get all pending leave applications.
    
    Args:
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
        
        # Get pending leaves
        leaves = await db_ops.find_many(
            "leaves",
            query={"status": "pending"},
            skip=skip,
            limit=page_size,
            sort=[("createdAt", 1)]
        )
        
        # Get total count
        total_count = await db_ops.count_documents("leaves", {"status": "pending"})
        
        # Format leaves data
        formatted_leaves = [format_leave_data(leave) for leave in leaves]
        
        return format_paginated_response(
            formatted_leaves,
            page,
            page_size,
            total_count,
            f"Retrieved {len(formatted_leaves)} pending leave applications"
        )
        
    except Exception as e:
        logger.error(f"Error getting pending leaves: {e}")
        return format_error_response(e, "Failed to retrieve pending leaves")


async def get_leave_statistics() -> Dict[str, Any]:
    """
    Get leave statistics and analytics.
    """
    try:
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get total leaves count
        total_leaves = await db_ops.count_documents("leaves", {})
        
        # Get leaves by status
        status_stats = await db_ops.aggregate("leaves", [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ])
        
        # Get leaves by month
        monthly_stats = await db_ops.aggregate("leaves", [
            {"$group": {
                "_id": {
                    "year": {"$year": "$createdAt"},
                    "month": {"$month": "$createdAt"}
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}},
            {"$limit": 12}
        ])
        
        # Get average leave duration
        duration_stats = await db_ops.aggregate("leaves", [
            {"$project": {
                "duration": {
                    "$divide": [
                        {"$subtract": ["$endDate", "$startDate"]},
                        86400000  # Convert milliseconds to days
                    ]
                }
            }},
            {"$group": {
                "_id": None,
                "avg_duration": {"$avg": "$duration"}
            }}
        ])
        
        statistics = {
            "total_leaves": total_leaves,
            "status_distribution": {stat["_id"]: stat["count"] for stat in status_stats},
            "monthly_trends": [
                {
                    "year": stat["_id"]["year"],
                    "month": stat["_id"]["month"],
                    "count": stat["count"]
                }
                for stat in monthly_stats
            ],
            "average_duration_days": round(duration_stats[0].get("avg_duration", 0), 2) if duration_stats else 0
        }
        
        return format_success_response(
            statistics,
            "Leave statistics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting leave statistics: {e}")
        return format_error_response(e, "Failed to retrieve leave statistics")


# MCP Tool definitions
def get_leave_tools() -> List[Tool]:
    """Get all leave management tools."""
    return [
        Tool(
            name="get_leaves",
            description="Get list of leave applications with optional filtering and pagination",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "default": 1, "description": "Page number"},
                    "page_size": {"type": "integer", "default": 50, "description": "Number of items per page"},
                    "status": {"type": "string", "enum": ["pending", "approved", "rejected", "cancelled"], "description": "Filter by status"},
                    "sort_by": {"type": "string", "default": "createdAt", "description": "Field to sort by"},
                    "sort_order": {"type": "string", "enum": ["asc", "desc"], "default": "desc", "description": "Sort order"}
                }
            }
        ),
        Tool(
            name="get_leave_by_id",
            description="Get specific leave application by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "leave_id": {"type": "string", "description": "Leave ObjectId"}
                },
                "required": ["leave_id"]
            }
        ),
        Tool(
            name="create_leave",
            description="Create new leave application",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {"type": "string", "description": "Student ObjectId"},
                    "start_date": {"type": "string", "description": "Start date in ISO format"},
                    "end_date": {"type": "string", "description": "End date in ISO format"},
                    "reason": {"type": "string", "description": "Leave reason"},
                    "status": {"type": "string", "enum": ["pending", "approved", "rejected", "cancelled"], "default": "pending", "description": "Leave status"}
                },
                "required": ["student_id", "start_date", "end_date", "reason"]
            }
        ),
        Tool(
            name="update_leave",
            description="Update existing leave application",
            inputSchema={
                "type": "object",
                "properties": {
                    "leave_id": {"type": "string", "description": "Leave ObjectId"},
                    "start_date": {"type": "string", "description": "Updated start date (optional)"},
                    "end_date": {"type": "string", "description": "Updated end date (optional)"},
                    "reason": {"type": "string", "description": "Updated reason (optional)"},
                    "status": {"type": "string", "enum": ["pending", "approved", "rejected", "cancelled"], "description": "Updated status (optional)"},
                    "handled_by": {"type": "string", "description": "Faculty ObjectId who handled (optional)"},
                    "remarks": {"type": "string", "description": "Updated remarks (optional)"}
                },
                "required": ["leave_id"]
            }
        ),
        Tool(
            name="delete_leave",
            description="Delete leave application",
            inputSchema={
                "type": "object",
                "properties": {
                    "leave_id": {"type": "string", "description": "Leave ObjectId"}
                },
                "required": ["leave_id"]
            }
        ),
        Tool(
            name="approve_leave",
            description="Approve leave application",
            inputSchema={
                "type": "object",
                "properties": {
                    "leave_id": {"type": "string", "description": "Leave ObjectId"},
                    "handled_by": {"type": "string", "description": "Faculty ObjectId who approved"},
                    "remarks": {"type": "string", "description": "Optional remarks"}
                },
                "required": ["leave_id", "handled_by"]
            }
        ),
        Tool(
            name="reject_leave",
            description="Reject leave application",
            inputSchema={
                "type": "object",
                "properties": {
                    "leave_id": {"type": "string", "description": "Leave ObjectId"},
                    "handled_by": {"type": "string", "description": "Faculty ObjectId who rejected"},
                    "remarks": {"type": "string", "description": "Rejection reason (required)"}
                },
                "required": ["leave_id", "handled_by", "remarks"]
            }
        ),
        Tool(
            name="get_leaves_by_student",
            description="Get leave applications for a specific student",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {"type": "string", "description": "Student ObjectId"},
                    "page": {"type": "integer", "default": 1, "description": "Page number"},
                    "page_size": {"type": "integer", "default": 50, "description": "Number of items per page"},
                    "status": {"type": "string", "enum": ["pending", "approved", "rejected", "cancelled"], "description": "Filter by status"}
                },
                "required": ["student_id"]
            }
        ),
        Tool(
            name="get_pending_leaves",
            description="Get all pending leave applications",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "default": 1, "description": "Page number"},
                    "page_size": {"type": "integer", "default": 50, "description": "Number of items per page"}
                }
            }
        ),
        Tool(
            name="get_leave_statistics",
            description="Get leave statistics and analytics",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]
