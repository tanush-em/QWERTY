"""
Timetable management tools for CSE-AIML ERP MCP Server.
"""
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, time
from mcp import Tool

from database import get_db_operations
from utils.validators import (
    validate_timetable_data, validate_object_id, validate_pagination_params,
    validate_day_of_week, validate_time_format, validate_course_code
)
from utils.formatters import (
    format_timetable_data, format_success_response, format_error_response,
    format_paginated_response
)

logger = logging.getLogger(__name__)


async def get_timetable(
    page: int = 1,
    page_size: int = 50,
    day_of_week: Optional[str] = None,
    sort_by: str = "dayOfWeek",
    sort_order: str = "asc"
) -> Dict[str, Any]:
    """
    Get complete timetable with optional filtering and pagination.
    
    Args:
        page: Page number (default: 1)
        page_size: Number of items per page (default: 50)
        day_of_week: Filter by day of week
        sort_by: Field to sort by (default: dayOfWeek)
        sort_order: Sort order - asc or desc (default: asc)
    """
    try:
        # Validate pagination parameters
        page, page_size = validate_pagination_params(page, page_size)
        
        # Build query
        query = {}
        if day_of_week and validate_day_of_week(day_of_week):
            query["dayOfWeek"] = day_of_week.lower()
        
        # Build sort
        sort_direction = 1 if sort_order.lower() == "asc" else -1
        sort = [(sort_by, sort_direction)]
        
        # Calculate skip
        skip = (page - 1) * page_size
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get timetable
        timetables = await db_ops.find_many(
            "timetables",
            query=query,
            skip=skip,
            limit=page_size,
            sort=sort
        )
        
        # Get total count
        total_count = await db_ops.count_documents("timetables", query)
        
        # Format timetable data
        formatted_timetables = [format_timetable_data(timetable) for timetable in timetables]
        
        return format_paginated_response(
            formatted_timetables,
            page,
            page_size,
            total_count,
            f"Retrieved {len(formatted_timetables)} timetable entries"
        )
        
    except Exception as e:
        logger.error(f"Error getting timetable: {e}")
        return format_error_response(e, "Failed to retrieve timetable")


async def get_timetable_by_day(day_of_week: str) -> Dict[str, Any]:
    """
    Get timetable for a specific day.
    
    Args:
        day_of_week: Day of week (monday, tuesday, etc.)
    """
    try:
        # Validate day of week
        if not validate_day_of_week(day_of_week):
            return format_error_response(
                ValueError("Invalid day of week"),
                "Invalid day of week format"
            )
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get timetable for specific day
        timetable = await db_ops.find_one("timetables", {"dayOfWeek": day_of_week.lower()})
        
        if not timetable:
            return format_error_response(
                ValueError("Timetable not found"),
                f"No timetable found for {day_of_week}"
            )
        
        # Format timetable data
        formatted_timetable = format_timetable_data(timetable)
        
        return format_success_response(
            formatted_timetable,
            f"Timetable for {day_of_week} retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting timetable by day: {e}")
        return format_error_response(e, "Failed to retrieve timetable for day")


async def create_timetable_slot(
    day_of_week: str,
    period: int,
    start_time: str,
    end_time: str,
    slot_type: str,
    course_code: Optional[str] = None,
    faculty_id: Optional[str] = None,
    room: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create new timetable slot.
    
    Args:
        day_of_week: Day of week
        period: Period number
        start_time: Start time (HH:MM)
        end_time: End time (HH:MM)
        slot_type: Type of slot (class, break, lunch, etc.)
        course_code: Course code (optional)
        faculty_id: Faculty ObjectId (optional)
        room: Room number/name (optional)
    """
    try:
        # Validate inputs
        if not validate_day_of_week(day_of_week):
            return format_error_response(
                ValueError("Invalid day of week"),
                "Invalid day of week format"
            )
        
        if not validate_time_format(start_time):
            return format_error_response(
                ValueError("Invalid start time"),
                "Invalid start time format (use HH:MM)"
            )
        
        if not validate_time_format(end_time):
            return format_error_response(
                ValueError("Invalid end time"),
                "Invalid end time format (use HH:MM)"
            )
        
        # Check time range
        start_time_obj = datetime.strptime(start_time, '%H:%M').time()
        end_time_obj = datetime.strptime(end_time, '%H:%M').time()
        if start_time_obj >= end_time_obj:
            return format_error_response(
                ValueError("Invalid time range"),
                "Start time must be before end time"
            )
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Check if timetable for this day already exists
        existing_timetable = await db_ops.find_one("timetables", {"dayOfWeek": day_of_week.lower()})
        
        # Create new slot
        new_slot = {
            "period": period,
            "startTime": start_time,
            "endTime": end_time,
            "type": slot_type,
            "courseCode": course_code,
            "facultyId": faculty_id,
            "room": room
        }
        
        if existing_timetable:
            # Add slot to existing timetable
            success = await db_ops.update_one(
                "timetables",
                {"_id": existing_timetable["_id"]},
                {
                    "$push": {"slots": new_slot},
                    "$set": {"updatedAt": datetime.now()}
                }
            )
        else:
            # Create new timetable entry
            timetable_data = {
                "dayOfWeek": day_of_week.lower(),
                "slots": [new_slot],
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            }
            
            await db_ops.insert_one("timetables", timetable_data)
            success = True
        
        if not success:
            return format_error_response(
                ValueError("Create failed"),
                "Failed to create timetable slot"
            )
        
        # Get updated timetable
        updated_timetable = await db_ops.find_one("timetables", {"dayOfWeek": day_of_week.lower()})
        formatted_timetable = format_timetable_data(updated_timetable)
        
        return format_success_response(
            formatted_timetable,
            f"Timetable slot created successfully for {day_of_week}"
        )
        
    except Exception as e:
        logger.error(f"Error creating timetable slot: {e}")
        return format_error_response(e, "Failed to create timetable slot")


async def update_timetable_slot(
    day_of_week: str,
    period: int,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    slot_type: Optional[str] = None,
    course_code: Optional[str] = None,
    faculty_id: Optional[str] = None,
    room: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update existing timetable slot.
    
    Args:
        day_of_week: Day of week
        period: Period number
        start_time: Updated start time (optional)
        end_time: Updated end time (optional)
        slot_type: Updated slot type (optional)
        course_code: Updated course code (optional)
        faculty_id: Updated faculty ID (optional)
        room: Updated room (optional)
    """
    try:
        # Validate day of week
        if not validate_day_of_week(day_of_week):
            return format_error_response(
                ValueError("Invalid day of week"),
                "Invalid day of week format"
            )
        
        # Validate time formats if provided
        if start_time and not validate_time_format(start_time):
            return format_error_response(
                ValueError("Invalid start time"),
                "Invalid start time format (use HH:MM)"
            )
        
        if end_time and not validate_time_format(end_time):
            return format_error_response(
                ValueError("Invalid end time"),
                "Invalid end time format (use HH:MM)"
            )
        
        # Check time range if both times provided
        if start_time and end_time:
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()
            if start_time_obj >= end_time_obj:
                return format_error_response(
                    ValueError("Invalid time range"),
                    "Start time must be before end time"
                )
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Find timetable for this day
        timetable = await db_ops.find_one("timetables", {"dayOfWeek": day_of_week.lower()})
        if not timetable:
            return format_error_response(
                ValueError("Timetable not found"),
                f"No timetable found for {day_of_week}"
            )
        
        # Find the slot to update
        slot_index = None
        for i, slot in enumerate(timetable.get("slots", [])):
            if slot.get("period") == period:
                slot_index = i
                break
        
        if slot_index is None:
            return format_error_response(
                ValueError("Slot not found"),
                f"No slot found for period {period} on {day_of_week}"
            )
        
        # Prepare update data
        update_fields = {}
        if start_time is not None:
            update_fields[f"slots.{slot_index}.startTime"] = start_time
        if end_time is not None:
            update_fields[f"slots.{slot_index}.endTime"] = end_time
        if slot_type is not None:
            update_fields[f"slots.{slot_index}.type"] = slot_type
        if course_code is not None:
            update_fields[f"slots.{slot_index}.courseCode"] = course_code
        if faculty_id is not None:
            update_fields[f"slots.{slot_index}.facultyId"] = faculty_id
        if room is not None:
            update_fields[f"slots.{slot_index}.room"] = room
        
        if not update_fields:
            return format_error_response(
                ValueError("No update data provided"),
                "No update data provided"
            )
        
        update_fields["updatedAt"] = datetime.now()
        
        # Update timetable slot
        success = await db_ops.update_one(
            "timetables",
            {"_id": timetable["_id"]},
            {"$set": update_fields}
        )
        
        if not success:
            return format_error_response(
                ValueError("Update failed"),
                "Failed to update timetable slot"
            )
        
        # Get updated timetable
        updated_timetable = await db_ops.find_one("timetables", {"_id": timetable["_id"]})
        formatted_timetable = format_timetable_data(updated_timetable)
        
        return format_success_response(
            formatted_timetable,
            f"Timetable slot updated successfully for {day_of_week}"
        )
        
    except Exception as e:
        logger.error(f"Error updating timetable slot: {e}")
        return format_error_response(e, "Failed to update timetable slot")


async def delete_timetable_slot(day_of_week: str, period: int) -> Dict[str, Any]:
    """
    Delete timetable slot.
    
    Args:
        day_of_week: Day of week
        period: Period number
    """
    try:
        # Validate day of week
        if not validate_day_of_week(day_of_week):
            return format_error_response(
                ValueError("Invalid day of week"),
                "Invalid day of week format"
            )
        
        # Get database operations
        db_ops = await get_db_operations()
        
        # Find timetable for this day
        timetable = await db_ops.find_one("timetables", {"dayOfWeek": day_of_week.lower()})
        if not timetable:
            return format_error_response(
                ValueError("Timetable not found"),
                f"No timetable found for {day_of_week}"
            )
        
        # Find the slot to delete
        slot_index = None
        for i, slot in enumerate(timetable.get("slots", [])):
            if slot.get("period") == period:
                slot_index = i
                break
        
        if slot_index is None:
            return format_error_response(
                ValueError("Slot not found"),
                f"No slot found for period {period} on {day_of_week}"
            )
        
        # Delete the slot
        success = await db_ops.update_one(
            "timetables",
            {"_id": timetable["_id"]},
            {
                "$unset": {f"slots.{slot_index}": 1},
                "$pull": {"slots": None},
                "$set": {"updatedAt": datetime.now()}
            }
        )
        
        if not success:
            return format_error_response(
                ValueError("Delete failed"),
                "Failed to delete timetable slot"
            )
        
        # Get updated timetable
        updated_timetable = await db_ops.find_one("timetables", {"_id": timetable["_id"]})
        formatted_timetable = format_timetable_data(updated_timetable)
        
        return format_success_response(
            formatted_timetable,
            f"Timetable slot deleted successfully for {day_of_week}"
        )
        
    except Exception as e:
        logger.error(f"Error deleting timetable slot: {e}")
        return format_error_response(e, "Failed to delete timetable slot")


async def get_faculty_schedule(faculty_id: str) -> Dict[str, Any]:
    """
    Get timetable schedule for a specific faculty member.
    
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
        
        # Get all timetables with slots for this faculty
        timetables = await db_ops.aggregate("timetables", [
            {"$unwind": "$slots"},
            {"$match": {"slots.facultyId": faculty_id}},
            {"$group": {
                "_id": "$_id",
                "dayOfWeek": {"$first": "$dayOfWeek"},
                "slots": {"$push": "$slots"},
                "createdAt": {"$first": "$createdAt"},
                "updatedAt": {"$first": "$updatedAt"}
            }},
            {"$sort": {"dayOfWeek": 1}}
        ])
        
        # Format faculty schedule
        faculty_schedule = {
            "faculty": {
                "id": str(faculty["_id"]),
                "employeeId": faculty.get("employeeId"),
                "fullName": faculty.get("fullName")
            },
            "schedule": [format_timetable_data(timetable) for timetable in timetables]
        }
        
        return format_success_response(
            faculty_schedule,
            f"Faculty schedule retrieved for {faculty.get('employeeId')}"
        )
        
    except Exception as e:
        logger.error(f"Error getting faculty schedule: {e}")
        return format_error_response(e, "Failed to retrieve faculty schedule")


async def check_room_availability(
    room: str,
    day_of_week: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
) -> Dict[str, Any]:
    """
    Check room availability and detect conflicts.
    
    Args:
        room: Room number/name
        day_of_week: Day to check (optional)
        start_time: Start time to check (optional)
        end_time: End time to check (optional)
    """
    try:
        # Get database operations
        db_ops = await get_db_operations()
        
        # Build query for room conflicts
        query = {"slots.room": room}
        
        if day_of_week and validate_day_of_week(day_of_week):
            query["dayOfWeek"] = day_of_week.lower()
        
        # Get all slots for this room
        timetables = await db_ops.find_many("timetables", query)
        
        conflicts = []
        available_slots = []
        
        for timetable in timetables:
            day = timetable.get("dayOfWeek")
            for slot in timetable.get("slots", []):
                if slot.get("room") == room:
                    slot_info = {
                        "dayOfWeek": day,
                        "period": slot.get("period"),
                        "startTime": slot.get("startTime"),
                        "endTime": slot.get("endTime"),
                        "type": slot.get("type"),
                        "courseCode": slot.get("courseCode"),
                        "facultyId": slot.get("facultyId")
                    }
                    
                    # Check for specific time conflict if provided
                    if start_time and end_time:
                        slot_start = datetime.strptime(slot.get("startTime", ""), '%H:%M').time()
                        slot_end = datetime.strptime(slot.get("endTime", ""), '%H:%M').time()
                        check_start = datetime.strptime(start_time, '%H:%M').time()
                        check_end = datetime.strptime(end_time, '%H:%M').time()
                        
                        # Check for time overlap
                        if (check_start < slot_end and check_end > slot_start):
                            conflicts.append(slot_info)
                    else:
                        conflicts.append(slot_info)
        
        # Find available slots (simplified - assumes 8 periods per day)
        if not start_time or not end_time:
            all_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
            for day in all_days:
                if day_of_week and day != day_of_week.lower():
                    continue
                
                day_timetable = next((t for t in timetables if t.get("dayOfWeek") == day), None)
                occupied_periods = set()
                
                if day_timetable:
                    for slot in day_timetable.get("slots", []):
                        if slot.get("room") == room:
                            occupied_periods.add(slot.get("period"))
                
                # Find free periods
                for period in range(1, 9):
                    if period not in occupied_periods:
                        available_slots.append({
                            "dayOfWeek": day,
                            "period": period,
                            "status": "available"
                        })
        
        availability_info = {
            "room": room,
            "conflicts": conflicts,
            "available_slots": available_slots,
            "total_conflicts": len(conflicts),
            "total_available": len(available_slots)
        }
        
        return format_success_response(
            availability_info,
            f"Room availability checked for {room}"
        )
        
    except Exception as e:
        logger.error(f"Error checking room availability: {e}")
        return format_error_response(e, "Failed to check room availability")


async def get_free_periods(
    day_of_week: Optional[str] = None,
    faculty_id: Optional[str] = None,
    room: Optional[str] = None
) -> Dict[str, Any]:
    """
    Find free periods in the timetable.
    
    Args:
        day_of_week: Day to check (optional)
        faculty_id: Faculty ID to check (optional)
        room: Room to check (optional)
    """
    try:
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get all timetables
        query = {}
        if day_of_week and validate_day_of_week(day_of_week):
            query["dayOfWeek"] = day_of_week.lower()
        
        timetables = await db_ops.find_many("timetables", query)
        
        free_periods = []
        days_to_check = [day_of_week.lower()] if day_of_week else ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        
        for day in days_to_check:
            if day_of_week and day != day_of_week.lower():
                continue
            
            # Find timetable for this day
            day_timetable = next((t for t in timetables if t.get("dayOfWeek") == day), None)
            
            if not day_timetable:
                # All periods are free if no timetable exists for this day
                for period in range(1, 9):
                    free_periods.append({
                        "dayOfWeek": day,
                        "period": period,
                        "startTime": f"{8 + period}:00",  # Assuming 9 AM start
                        "endTime": f"{9 + period}:00",
                        "status": "completely_free"
                    })
                continue
            
            # Find occupied periods based on criteria
            occupied_periods = set()
            
            for slot in day_timetable.get("slots", []):
                if faculty_id and slot.get("facultyId") == faculty_id:
                    occupied_periods.add(slot.get("period"))
                elif room and slot.get("room") == room:
                    occupied_periods.add(slot.get("period"))
                elif not faculty_id and not room:
                    # If no specific criteria, all occupied periods
                    occupied_periods.add(slot.get("period"))
            
            # Find free periods
            for period in range(1, 9):
                if period not in occupied_periods:
                    free_periods.append({
                        "dayOfWeek": day,
                        "period": period,
                        "startTime": f"{8 + period}:00",  # Assuming 9 AM start
                        "endTime": f"{9 + period}:00",
                        "status": "free"
                    })
        
        # Sort by day and period
        free_periods.sort(key=lambda x: (x["dayOfWeek"], x["period"]))
        
        return format_success_response(
            {
                "free_periods": free_periods,
                "total_free": len(free_periods),
                "criteria": {
                    "day_of_week": day_of_week,
                    "faculty_id": faculty_id,
                    "room": room
                }
            },
            f"Found {len(free_periods)} free periods"
        )
        
    except Exception as e:
        logger.error(f"Error getting free periods: {e}")
        return format_error_response(e, "Failed to get free periods")


# MCP Tool definitions
def get_timetable_tools() -> List[Tool]:
    """Get all timetable management tools."""
    return [
        Tool(
            name="get_timetable",
            description="Get complete timetable with optional filtering and pagination",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "default": 1, "description": "Page number"},
                    "page_size": {"type": "integer", "default": 50, "description": "Number of items per page"},
                    "day_of_week": {"type": "string", "enum": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"], "description": "Filter by day of week"},
                    "sort_by": {"type": "string", "default": "dayOfWeek", "description": "Field to sort by"},
                    "sort_order": {"type": "string", "enum": ["asc", "desc"], "default": "asc", "description": "Sort order"}
                }
            }
        ),
        Tool(
            name="get_timetable_by_day",
            description="Get timetable for a specific day",
            inputSchema={
                "type": "object",
                "properties": {
                    "day_of_week": {"type": "string", "enum": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"], "description": "Day of week"}
                },
                "required": ["day_of_week"]
            }
        ),
        Tool(
            name="create_timetable_slot",
            description="Create new timetable slot",
            inputSchema={
                "type": "object",
                "properties": {
                    "day_of_week": {"type": "string", "enum": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"], "description": "Day of week"},
                    "period": {"type": "integer", "description": "Period number"},
                    "start_time": {"type": "string", "description": "Start time (HH:MM)"},
                    "end_time": {"type": "string", "description": "End time (HH:MM)"},
                    "slot_type": {"type": "string", "description": "Type of slot (class, break, lunch, etc.)"},
                    "course_code": {"type": "string", "description": "Course code (optional)"},
                    "faculty_id": {"type": "string", "description": "Faculty ObjectId (optional)"},
                    "room": {"type": "string", "description": "Room number/name (optional)"}
                },
                "required": ["day_of_week", "period", "start_time", "end_time", "slot_type"]
            }
        ),
        Tool(
            name="update_timetable_slot",
            description="Update existing timetable slot",
            inputSchema={
                "type": "object",
                "properties": {
                    "day_of_week": {"type": "string", "enum": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"], "description": "Day of week"},
                    "period": {"type": "integer", "description": "Period number"},
                    "start_time": {"type": "string", "description": "Updated start time (optional)"},
                    "end_time": {"type": "string", "description": "Updated end time (optional)"},
                    "slot_type": {"type": "string", "description": "Updated slot type (optional)"},
                    "course_code": {"type": "string", "description": "Updated course code (optional)"},
                    "faculty_id": {"type": "string", "description": "Updated faculty ID (optional)"},
                    "room": {"type": "string", "description": "Updated room (optional)"}
                },
                "required": ["day_of_week", "period"]
            }
        ),
        Tool(
            name="delete_timetable_slot",
            description="Delete timetable slot",
            inputSchema={
                "type": "object",
                "properties": {
                    "day_of_week": {"type": "string", "enum": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"], "description": "Day of week"},
                    "period": {"type": "integer", "description": "Period number"}
                },
                "required": ["day_of_week", "period"]
            }
        ),
        Tool(
            name="get_faculty_schedule",
            description="Get timetable schedule for a specific faculty member",
            inputSchema={
                "type": "object",
                "properties": {
                    "faculty_id": {"type": "string", "description": "Faculty ObjectId"}
                },
                "required": ["faculty_id"]
            }
        ),
        Tool(
            name="check_room_availability",
            description="Check room availability and detect conflicts",
            inputSchema={
                "type": "object",
                "properties": {
                    "room": {"type": "string", "description": "Room number/name"},
                    "day_of_week": {"type": "string", "enum": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"], "description": "Day to check (optional)"},
                    "start_time": {"type": "string", "description": "Start time to check (optional)"},
                    "end_time": {"type": "string", "description": "End time to check (optional)"}
                },
                "required": ["room"]
            }
        ),
        Tool(
            name="get_free_periods",
            description="Find free periods in the timetable",
            inputSchema={
                "type": "object",
                "properties": {
                    "day_of_week": {"type": "string", "enum": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"], "description": "Day to check (optional)"},
                    "faculty_id": {"type": "string", "description": "Faculty ID to check (optional)"},
                    "room": {"type": "string", "description": "Room to check (optional)"}
                }
            }
        )
    ]
