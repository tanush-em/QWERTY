"""
Data formatting utilities for CSE-AIML ERP MCP Server.
"""
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from bson import ObjectId

logger = logging.getLogger(__name__)


def format_date(date_obj: Union[str, datetime, date]) -> str:
    """Format date object to ISO string."""
    if isinstance(date_obj, str):
        return date_obj
    
    if isinstance(date_obj, datetime):
        return date_obj.isoformat()
    
    if isinstance(date_obj, date):
        return date_obj.isoformat()
    
    return str(date_obj)


def format_datetime(datetime_obj: Union[str, datetime]) -> str:
    """Format datetime object to ISO string."""
    if isinstance(datetime_obj, str):
        return datetime_obj
    
    if isinstance(datetime_obj, datetime):
        return datetime_obj.isoformat()
    
    return str(datetime_obj)


def format_object_id(object_id: Union[str, ObjectId]) -> str:
    """Format ObjectId to string."""
    if isinstance(object_id, ObjectId):
        return str(object_id)
    
    return str(object_id)


def format_response(
    success: bool,
    data: Any = None,
    message: str = "",
    errors: List[str] = None,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Format standard API response."""
    response = {
        "success": success,
        "timestamp": datetime.now().isoformat()
    }
    
    if data is not None:
        response["data"] = data
    
    if message:
        response["message"] = message
    
    if errors:
        response["errors"] = errors
    
    if metadata:
        response["metadata"] = metadata
    
    return response


def format_error_response(error: Exception, message: str = None) -> Dict[str, Any]:
    """Format error response."""
    error_message = message or str(error)
    
    return format_response(
        success=False,
        message=error_message,
        errors=[error_message]
    )


def format_success_response(data: Any = None, message: str = "Operation completed successfully") -> Dict[str, Any]:
    """Format success response."""
    return format_response(
        success=True,
        data=data,
        message=message
    )


def format_paginated_response(
    data: List[Dict[str, Any]],
    page: int,
    page_size: int,
    total_count: int,
    message: str = "Data retrieved successfully"
) -> Dict[str, Any]:
    """Format paginated response."""
    total_pages = (total_count + page_size - 1) // page_size
    
    metadata = {
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
        }
    }
    
    return format_response(
        success=True,
        data=data,
        message=message,
        metadata=metadata
    )


def format_student_data(student: Dict[str, Any]) -> Dict[str, Any]:
    """Format student data for response."""
    if not student:
        return {}
    
    formatted = {
        "id": format_object_id(student.get("_id")),
        "roll": student.get("roll"),
        "fullName": student.get("fullName"),
        "email": student.get("email"),
        "phone": student.get("phone"),
        "year": student.get("year"),
        "batch": student.get("batch"),
        "dateOfBirth": format_date(student.get("dateOfBirth")),
        "createdAt": format_datetime(student.get("createdAt")),
        "updatedAt": format_datetime(student.get("updatedAt"))
    }
    
    # Remove None values
    return {k: v for k, v in formatted.items() if v is not None}


def format_faculty_data(faculty: Dict[str, Any]) -> Dict[str, Any]:
    """Format faculty data for response."""
    if not faculty:
        return {}
    
    formatted = {
        "id": format_object_id(faculty.get("_id")),
        "employeeId": faculty.get("employeeId"),
        "fullName": faculty.get("fullName"),
        "email": faculty.get("email"),
        "phone": faculty.get("phone"),
        "designation": faculty.get("designation"),
        "subjects": faculty.get("subjects", []),
        "createdAt": format_datetime(faculty.get("createdAt")),
        "updatedAt": format_datetime(faculty.get("updatedAt"))
    }
    
    # Remove None values
    return {k: v for k, v in formatted.items() if v is not None}


def format_course_data(course: Dict[str, Any]) -> Dict[str, Any]:
    """Format course data for response."""
    if not course:
        return {}
    
    formatted = {
        "id": format_object_id(course.get("_id")),
        "code": course.get("code"),
        "title": course.get("title"),
        "credits": course.get("credits"),
        "semester": course.get("semester"),
        "facultyInCharge": format_object_id(course.get("facultyInCharge")) if course.get("facultyInCharge") else None,
        "description": course.get("description"),
        "createdAt": format_datetime(course.get("createdAt")),
        "updatedAt": format_datetime(course.get("updatedAt"))
    }
    
    # Remove None values
    return {k: v for k, v in formatted.items() if v is not None}


def format_leave_data(leave: Dict[str, Any]) -> Dict[str, Any]:
    """Format leave application data for response."""
    if not leave:
        return {}
    
    formatted = {
        "id": format_object_id(leave.get("_id")),
        "studentId": format_object_id(leave.get("studentId")) if leave.get("studentId") else None,
        "startDate": format_date(leave.get("startDate")),
        "endDate": format_date(leave.get("endDate")),
        "reason": leave.get("reason"),
        "status": leave.get("status"),
        "handledBy": format_object_id(leave.get("handledBy")) if leave.get("handledBy") else None,
        "remarks": leave.get("remarks"),
        "createdAt": format_datetime(leave.get("createdAt")),
        "updatedAt": format_datetime(leave.get("updatedAt"))
    }
    
    # Remove None values
    return {k: v for k, v in formatted.items() if v is not None}


def format_timetable_data(timetable: Dict[str, Any]) -> Dict[str, Any]:
    """Format timetable data for response."""
    if not timetable:
        return {}
    
    formatted = {
        "id": format_object_id(timetable.get("_id")),
        "dayOfWeek": timetable.get("dayOfWeek"),
        "slots": timetable.get("slots", []),
        "createdAt": format_datetime(timetable.get("createdAt")),
        "updatedAt": format_datetime(timetable.get("updatedAt"))
    }
    
    return formatted


def format_analytics_data(analytics: Dict[str, Any]) -> Dict[str, Any]:
    """Format analytics data for response."""
    if not analytics:
        return {}
    
    # Format any ObjectIds in the analytics data
    formatted = {}
    for key, value in analytics.items():
        if isinstance(value, ObjectId):
            formatted[key] = format_object_id(value)
        elif isinstance(value, dict):
            formatted[key] = format_analytics_data(value)
        elif isinstance(value, list):
            formatted[key] = [
                format_analytics_data(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            formatted[key] = value
    
    return formatted


def format_csv_row(data: Dict[str, Any], headers: List[str]) -> Dict[str, str]:
    """Format data row for CSV export."""
    row = {}
    for header in headers:
        value = data.get(header, "")
        if isinstance(value, (list, dict)):
            value = str(value)
        elif isinstance(value, ObjectId):
            value = format_object_id(value)
        elif isinstance(value, datetime):
            value = format_datetime(value)
        elif isinstance(value, date):
            value = format_date(value)
        else:
            value = str(value) if value is not None else ""
        
        row[header] = value
    
    return row


def format_search_result(
    result: Dict[str, Any],
    search_term: str,
    matched_fields: List[str] = None
) -> Dict[str, Any]:
    """Format search result with highlighting information."""
    formatted = result.copy()
    formatted["_search_metadata"] = {
        "search_term": search_term,
        "matched_fields": matched_fields or []
    }
    
    return formatted


def format_aggregation_result(
    results: List[Dict[str, Any]],
    operation: str,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Format aggregation query results."""
    return {
        "operation": operation,
        "results": results,
        "count": len(results),
        "metadata": metadata or {},
        "timestamp": datetime.now().isoformat()
    }


def format_bulk_operation_result(
    operation: str,
    success_count: int,
    error_count: int,
    errors: List[str] = None
) -> Dict[str, Any]:
    """Format bulk operation result."""
    return {
        "operation": operation,
        "success_count": success_count,
        "error_count": error_count,
        "total_count": success_count + error_count,
        "errors": errors or [],
        "timestamp": datetime.now().isoformat()
    }


def sanitize_for_logging(data: Any) -> Any:
    """Sanitize sensitive data for logging."""
    if isinstance(data, dict):
        sanitized = {}
        sensitive_fields = {'password', 'token', 'secret', 'key'}
        
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = sanitize_for_logging(value)
            elif isinstance(value, list):
                sanitized[key] = [sanitize_for_logging(item) if isinstance(item, dict) else item for item in value]
            else:
                sanitized[key] = value
        
        return sanitized
    
    return data


def format_duration(start_time: datetime, end_time: datetime = None) -> str:
    """Format duration between two datetime objects."""
    if end_time is None:
        end_time = datetime.now()
    
    duration = end_time - start_time
    total_seconds = duration.total_seconds()
    
    if total_seconds < 60:
        return f"{total_seconds:.2f} seconds"
    elif total_seconds < 3600:
        minutes = total_seconds / 60
        return f"{minutes:.2f} minutes"
    else:
        hours = total_seconds / 3600
        return f"{hours:.2f} hours"
