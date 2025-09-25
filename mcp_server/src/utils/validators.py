"""
Input validation utilities for CSE-AIML ERP MCP Server.
"""
import re
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from bson import ObjectId
from bson.errors import InvalidId

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error."""
    pass


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    if not phone:
        return False
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (7-15 digits)
    return 7 <= len(digits) <= 15


def validate_object_id(object_id: str) -> bool:
    """Validate MongoDB ObjectId format."""
    if not object_id:
        return False
    
    try:
        ObjectId(object_id)
        return True
    except (InvalidId, TypeError):
        return False


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Validate that all required fields are present and not empty."""
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")


def validate_date_range(start_date: Union[str, date], end_date: Union[str, date]) -> None:
    """Validate that start date is before end date."""
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()
    
    if start_date >= end_date:
        raise ValidationError("Start date must be before end date")


def validate_date_format(date_string: str) -> bool:
    """Validate date format (ISO 8601)."""
    if not date_string:
        return False
    
    try:
        datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False


def validate_academic_year(year: Union[int, str]) -> bool:
    """Validate academic year format (e.g., 2024, "2024-25")."""
    if isinstance(year, int):
        return 2000 <= year <= 2100
    
    if isinstance(year, str):
        # Check for format like "2024-25"
        if '-' in year:
            parts = year.split('-')
            if len(parts) == 2:
                try:
                    start_year = int(parts[0])
                    end_year = int(parts[1])
                    return (2000 <= start_year <= 2100 and 
                           2000 <= end_year <= 2100 and
                           end_year == start_year + 1)
                except ValueError:
                    return False
        else:
            # Single year format
            try:
                year_int = int(year)
                return 2000 <= year_int <= 2100
            except ValueError:
                return False
    
    return False


def validate_roll_number(roll: str) -> bool:
    """Validate student roll number format."""
    if not roll:
        return False
    
    # Pattern: CSE followed by numbers (e.g., CSE001, CSE2024)
    pattern = r'^CSE\d{3,4}$'
    return bool(re.match(pattern, roll.upper()))


def validate_employee_id(employee_id: str) -> bool:
    """Validate faculty employee ID format."""
    if not employee_id:
        return False
    
    # Pattern: EMP followed by numbers (e.g., EMP001, EMP2024)
    pattern = r'^EMP\d{3,4}$'
    return bool(re.match(pattern, employee_id.upper()))


def validate_course_code(course_code: str) -> bool:
    """Validate course code format."""
    if not course_code:
        return False
    
    # Pattern: 3-6 letters followed by 3-4 numbers (e.g., CS101, MATH2024)
    pattern = r'^[A-Z]{3,6}\d{3,4}$'
    return bool(re.match(pattern, course_code.upper()))


def validate_credits(credits: Union[int, float]) -> bool:
    """Validate course credits (1-6 credits)."""
    try:
        credits_num = float(credits)
        return 1.0 <= credits_num <= 6.0
    except (ValueError, TypeError):
        return False


def validate_semester(semester: Union[int, str]) -> bool:
    """Validate semester number (1-8 for UG, 1-4 for PG)."""
    try:
        semester_num = int(semester)
        return 1 <= semester_num <= 8
    except (ValueError, TypeError):
        return False


def validate_day_of_week(day: str) -> bool:
    """Validate day of week."""
    valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    return day.lower() in valid_days


def validate_time_format(time_str: str) -> bool:
    """Validate time format (HH:MM)."""
    if not time_str:
        return False
    
    pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
    return bool(re.match(pattern, time_str))


def validate_pagination_params(page: int = 1, page_size: int = 50) -> tuple:
    """Validate and normalize pagination parameters."""
    try:
        page = max(1, int(page))
        page_size = max(1, min(1000, int(page_size)))  # Limit max page size
        return page, page_size
    except (ValueError, TypeError):
        return 1, 50


def validate_search_query(query: str) -> bool:
    """Validate search query (not empty, reasonable length)."""
    if not query or not isinstance(query, str):
        return False
    
    # Remove whitespace and check length
    clean_query = query.strip()
    return 1 <= len(clean_query) <= 100


def validate_leave_status(status: str) -> bool:
    """Validate leave application status."""
    valid_statuses = ['pending', 'approved', 'rejected', 'cancelled']
    return status.lower() in valid_statuses


def validate_leave_reason(reason: str) -> bool:
    """Validate leave reason (not empty, reasonable length)."""
    if not reason or not isinstance(reason, str):
        return False
    
    clean_reason = reason.strip()
    return 5 <= len(clean_reason) <= 500


def validate_student_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate student data and return validation errors."""
    errors = {}
    
    # Required fields
    try:
        validate_required_fields(data, ['roll', 'fullName', 'email', 'year'])
    except ValidationError as e:
        errors['required'] = [str(e)]
    
    # Email validation
    if 'email' in data and not validate_email(data['email']):
        errors['email'] = ['Invalid email format']
    
    # Phone validation
    if 'phone' in data and data['phone'] and not validate_phone(data['phone']):
        errors['phone'] = ['Invalid phone number format']
    
    # Roll number validation
    if 'roll' in data and not validate_roll_number(data['roll']):
        errors['roll'] = ['Invalid roll number format (should be CSE followed by 3-4 digits)']
    
    # Year validation
    if 'year' in data and not validate_academic_year(data['year']):
        errors['year'] = ['Invalid academic year format']
    
    # Date of birth validation
    if 'dateOfBirth' in data and data['dateOfBirth']:
        if not validate_date_format(data['dateOfBirth']):
            errors['dateOfBirth'] = ['Invalid date format (use ISO 8601 format)']
    
    return errors


def validate_faculty_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate faculty data and return validation errors."""
    errors = {}
    
    # Required fields
    try:
        validate_required_fields(data, ['employeeId', 'fullName', 'email', 'designation'])
    except ValidationError as e:
        errors['required'] = [str(e)]
    
    # Email validation
    if 'email' in data and not validate_email(data['email']):
        errors['email'] = ['Invalid email format']
    
    # Phone validation
    if 'phone' in data and data['phone'] and not validate_phone(data['phone']):
        errors['phone'] = ['Invalid phone number format']
    
    # Employee ID validation
    if 'employeeId' in data and not validate_employee_id(data['employeeId']):
        errors['employeeId'] = ['Invalid employee ID format (should be EMP followed by 3-4 digits)']
    
    return errors


def validate_course_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate course data and return validation errors."""
    errors = {}
    
    # Required fields
    try:
        validate_required_fields(data, ['code', 'title', 'credits', 'semester'])
    except ValidationError as e:
        errors['required'] = [str(e)]
    
    # Course code validation
    if 'code' in data and not validate_course_code(data['code']):
        errors['code'] = ['Invalid course code format (3-6 letters followed by 3-4 numbers)']
    
    # Credits validation
    if 'credits' in data and not validate_credits(data['credits']):
        errors['credits'] = ['Credits must be between 1 and 6']
    
    # Semester validation
    if 'semester' in data and not validate_semester(data['semester']):
        errors['semester'] = ['Semester must be between 1 and 8']
    
    return errors


def validate_leave_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate leave application data and return validation errors."""
    errors = {}
    
    # Required fields
    try:
        validate_required_fields(data, ['studentId', 'startDate', 'endDate', 'reason'])
    except ValidationError as e:
        errors['required'] = [str(e)]
    
    # Student ID validation
    if 'studentId' in data and not validate_object_id(data['studentId']):
        errors['studentId'] = ['Invalid student ID format']
    
    # Date validation
    if 'startDate' in data and not validate_date_format(data['startDate']):
        errors['startDate'] = ['Invalid start date format (use ISO 8601 format)']
    
    if 'endDate' in data and not validate_date_format(data['endDate']):
        errors['endDate'] = ['Invalid end date format (use ISO 8601 format)']
    
    # Date range validation
    if ('startDate' in data and 'endDate' in data and 
        validate_date_format(data['startDate']) and validate_date_format(data['endDate'])):
        try:
            validate_date_range(data['startDate'], data['endDate'])
        except ValidationError as e:
            errors['dateRange'] = [str(e)]
    
    # Reason validation
    if 'reason' in data and not validate_leave_reason(data['reason']):
        errors['reason'] = ['Leave reason must be between 5 and 500 characters']
    
    # Status validation
    if 'status' in data and data['status'] and not validate_leave_status(data['status']):
        errors['status'] = ['Invalid status (must be pending, approved, rejected, or cancelled)']
    
    return errors


def validate_timetable_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate timetable data and return validation errors."""
    errors = {}
    
    # Required fields
    try:
        validate_required_fields(data, ['dayOfWeek', 'slots'])
    except ValidationError as e:
        errors['required'] = [str(e)]
    
    # Day of week validation
    if 'dayOfWeek' in data and not validate_day_of_week(data['dayOfWeek']):
        errors['dayOfWeek'] = ['Invalid day of week']
    
    # Slots validation
    if 'slots' in data and isinstance(data['slots'], list):
        for i, slot in enumerate(data['slots']):
            slot_errors = []
            
            # Required slot fields
            required_slot_fields = ['period', 'startTime', 'endTime', 'type']
            try:
                validate_required_fields(slot, required_slot_fields)
            except ValidationError as e:
                slot_errors.append(str(e))
            
            # Time validation
            if 'startTime' in slot and not validate_time_format(slot['startTime']):
                slot_errors.append('Invalid start time format')
            
            if 'endTime' in slot and not validate_time_format(slot['endTime']):
                slot_errors.append('Invalid end time format')
            
            # Time range validation
            if ('startTime' in slot and 'endTime' in slot and 
                validate_time_format(slot['startTime']) and validate_time_format(slot['endTime'])):
                start_time = datetime.strptime(slot['startTime'], '%H:%M').time()
                end_time = datetime.strptime(slot['endTime'], '%H:%M').time()
                if start_time >= end_time:
                    slot_errors.append('Start time must be before end time')
            
            if slot_errors:
                errors[f'slot_{i}'] = slot_errors
    
    return errors
