"""
Analytics and reporting tools for CSE-AIML ERP MCP Server.
"""
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from mcp import Tool

from database import get_db_operations
from utils.formatters import format_success_response, format_error_response

logger = logging.getLogger(__name__)


async def get_enrollment_stats() -> Dict[str, Any]:
    """
    Get student enrollment statistics and analytics.
    """
    try:
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get total students count
        total_students = await db_ops.count_documents("students", {})
        
        # Get students by year
        year_stats = await db_ops.aggregate("students", [
            {"$group": {"_id": "$year", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ])
        
        # Get students by batch
        batch_stats = await db_ops.aggregate("students", [
            {"$group": {"_id": "$batch", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ])
        
        # Get enrollment trends by month
        enrollment_trends = await db_ops.aggregate("students", [
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
        
        # Get students with complete profiles
        students_with_email = await db_ops.count_documents("students", {"email": {"$exists": True, "$ne": None}})
        students_with_phone = await db_ops.count_documents("students", {"phone": {"$exists": True, "$ne": None}})
        students_with_dob = await db_ops.count_documents("students", {"dateOfBirth": {"$exists": True, "$ne": None}})
        
        enrollment_stats = {
            "total_students": total_students,
            "year_distribution": {stat["_id"]: stat["count"] for stat in year_stats if stat["_id"]},
            "batch_distribution": {stat["_id"]: stat["count"] for stat in batch_stats if stat["_id"]},
            "enrollment_trends": [
                {
                    "year": trend["_id"]["year"],
                    "month": trend["_id"]["month"],
                    "count": trend["count"]
                }
                for trend in enrollment_trends
            ],
            "profile_completeness": {
                "with_email": students_with_email,
                "with_phone": students_with_phone,
                "with_dob": students_with_dob,
                "email_percentage": round((students_with_email / total_students * 100), 2) if total_students > 0 else 0,
                "phone_percentage": round((students_with_phone / total_students * 100), 2) if total_students > 0 else 0,
                "dob_percentage": round((students_with_dob / total_students * 100), 2) if total_students > 0 else 0
            }
        }
        
        return format_success_response(
            enrollment_stats,
            "Enrollment statistics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting enrollment stats: {e}")
        return format_error_response(e, "Failed to retrieve enrollment statistics")


async def get_attendance_summary() -> Dict[str, Any]:
    """
    Get attendance summary statistics.
    Note: This is a placeholder implementation as attendance data structure wasn't specified.
    """
    try:
        # Get database operations
        db_ops = await get_db_operations()
        
        # Placeholder implementation - in a real system, you'd have attendance records
        attendance_summary = {
            "total_attendance_records": 0,
            "average_attendance_rate": 0,
            "attendance_by_course": [],
            "attendance_by_student": [],
            "attendance_trends": [],
            "low_attendance_students": [],
            "note": "Attendance tracking not implemented in current system"
        }
        
        return format_success_response(
            attendance_summary,
            "Attendance summary retrieved (placeholder implementation)"
        )
        
    except Exception as e:
        logger.error(f"Error getting attendance summary: {e}")
        return format_error_response(e, "Failed to retrieve attendance summary")


async def get_leave_analytics() -> Dict[str, Any]:
    """
    Get leave pattern analysis and statistics.
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
                "avg_duration": {"$avg": "$duration"},
                "min_duration": {"$min": "$duration"},
                "max_duration": {"$max": "$duration"}
            }}
        ])
        
        # Get most common leave reasons
        reason_stats = await db_ops.aggregate("leaves", [
            {"$group": {"_id": "$reason", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ])
        
        # Get leaves by student
        student_leave_stats = await db_ops.aggregate("leaves", [
            {"$group": {"_id": "$studentId", "leave_count": {"$sum": 1}}},
            {"$sort": {"leave_count": -1}},
            {"$limit": 10}
        ])
        
        leave_analytics = {
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
            "duration_analysis": {
                "average_days": round(duration_stats[0].get("avg_duration", 0), 2) if duration_stats else 0,
                "minimum_days": duration_stats[0].get("min_duration", 0) if duration_stats else 0,
                "maximum_days": duration_stats[0].get("max_duration", 0) if duration_stats else 0
            },
            "top_reasons": [
                {"reason": stat["_id"], "count": stat["count"]}
                for stat in reason_stats
            ],
            "top_students_by_leaves": [
                {"student_id": stat["_id"], "leave_count": stat["leave_count"]}
                for stat in student_leave_stats
            ]
        }
        
        return format_success_response(
            leave_analytics,
            "Leave analytics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting leave analytics: {e}")
        return format_error_response(e, "Failed to retrieve leave analytics")


async def get_faculty_workload_report() -> Dict[str, Any]:
    """
    Get faculty workload distribution and teaching load analysis.
    """
    try:
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get total faculty count
        total_faculty = await db_ops.count_documents("faculties", {})
        
        # Get faculty workload analysis
        faculty_workload = await db_ops.aggregate("faculties", [
            {"$lookup": {
                "from": "courses",
                "localField": "_id",
                "foreignField": "facultyInCharge",
                "as": "courses"
            }},
            {"$project": {
                "employeeId": 1,
                "fullName": 1,
                "designation": 1,
                "subjects": 1,
                "course_count": {"$size": "$courses"},
                "total_credits": {"$sum": "$courses.credits"}
            }},
            {"$sort": {"course_count": -1}}
        ])
        
        # Get faculty by designation
        designation_stats = await db_ops.aggregate("faculties", [
            {"$group": {"_id": "$designation", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ])
        
        # Get faculty with subjects
        faculty_subjects = await db_ops.aggregate("faculties", [
            {"$project": {
                "employeeId": 1,
                "fullName": 1,
                "subject_count": {"$size": {"$ifNull": ["$subjects", []]}}
            }},
            {"$sort": {"subject_count": -1}}
        ])
        
        # Get courses without faculty
        courses_without_faculty = await db_ops.count_documents("courses", {"facultyInCharge": {"$exists": False}})
        courses_with_faculty = await db_ops.count_documents("courses", {"facultyInCharge": {"$exists": True}})
        
        workload_report = {
            "total_faculty": total_faculty,
            "faculty_workload": [
                {
                    "employee_id": faculty["employeeId"],
                    "full_name": faculty["fullName"],
                    "designation": faculty["designation"],
                    "course_count": faculty["course_count"],
                    "total_credits": faculty["total_credits"],
                    "subject_count": len(faculty.get("subjects", []))
                }
                for faculty in faculty_workload
            ],
            "designation_distribution": {stat["_id"]: stat["count"] for stat in designation_stats},
            "faculty_by_subjects": [
                {
                    "employee_id": faculty["employeeId"],
                    "full_name": faculty["fullName"],
                    "subject_count": faculty["subject_count"]
                }
                for faculty in faculty_subjects
            ],
            "course_assignment": {
                "courses_with_faculty": courses_with_faculty,
                "courses_without_faculty": courses_without_faculty,
                "assignment_percentage": round((courses_with_faculty / (courses_with_faculty + courses_without_faculty) * 100), 2) if (courses_with_faculty + courses_without_faculty) > 0 else 0
            }
        }
        
        return format_success_response(
            workload_report,
            "Faculty workload report retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting faculty workload report: {e}")
        return format_error_response(e, "Failed to retrieve faculty workload report")


async def get_course_popularity() -> Dict[str, Any]:
    """
    Get course enrollment trends and popularity analysis.
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
        
        # Get courses by credits
        credit_stats = await db_ops.aggregate("courses", [
            {"$group": {"_id": "$credits", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ])
        
        # Get courses with faculty assigned
        courses_with_faculty = await db_ops.aggregate("courses", [
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
                "faculty_name": {"$arrayElemAt": ["$faculty.fullName", 0]},
                "faculty_id": "$facultyInCharge"
            }},
            {"$sort": {"semester": 1, "code": 1}}
        ])
        
        # Get courses without faculty
        courses_without_faculty = await db_ops.find_many("courses", {"facultyInCharge": {"$exists": False}})
        
        # Calculate total credits
        total_credits = await db_ops.aggregate("courses", [
            {"$group": {"_id": None, "total": {"$sum": "$credits"}}}
        ])
        
        course_popularity = {
            "total_courses": total_courses,
            "total_credits": total_credits[0].get("total", 0) if total_credits else 0,
            "semester_distribution": {stat["_id"]: stat["count"] for stat in semester_stats},
            "credit_distribution": {stat["_id"]: stat["count"] for stat in credit_stats},
            "courses_with_faculty": [
                {
                    "code": course["code"],
                    "title": course["title"],
                    "credits": course["credits"],
                    "semester": course["semester"],
                    "faculty_name": course.get("faculty_name"),
                    "faculty_id": course.get("faculty_id")
                }
                for course in courses_with_faculty
            ],
            "courses_without_faculty": [
                {
                    "code": course["code"],
                    "title": course["title"],
                    "credits": course["credits"],
                    "semester": course["semester"]
                }
                for course in courses_without_faculty
            ],
            "faculty_assignment_rate": round((len(courses_with_faculty) / total_courses * 100), 2) if total_courses > 0 else 0
        }
        
        return format_success_response(
            course_popularity,
            "Course popularity analysis retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting course popularity: {e}")
        return format_error_response(e, "Failed to retrieve course popularity analysis")


async def get_demographic_analysis() -> Dict[str, Any]:
    """
    Get student demographic analysis.
    """
    try:
        # Get database operations
        db_ops = await get_db_operations()
        
        # Get students by year
        year_demographics = await db_ops.aggregate("students", [
            {"$group": {
                "_id": "$year",
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ])
        
        # Get students by batch
        batch_demographics = await db_ops.aggregate("students", [
            {"$group": {
                "_id": "$batch",
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ])
        
        # Get age distribution (based on date of birth)
        age_demographics = await db_ops.aggregate("students", [
            {"$match": {"dateOfBirth": {"$exists": True, "$ne": None}}},
            {"$project": {
                "age": {
                    "$divide": [
                        {"$subtract": [datetime.now(), "$dateOfBirth"]},
                        31557600000  # Convert milliseconds to years
                    ]
                }
            }},
            {"$bucket": {
                "groupBy": "$age",
                "boundaries": [18, 20, 22, 24, 26, 28, 30],
                "default": "30+",
                "output": {"count": {"$sum": 1}}
            }}
        ])
        
        # Get students with complete contact information
        contact_completeness = await db_ops.aggregate("students", [
            {"$project": {
                "has_email": {"$cond": [{"$ne": ["$email", None]}, 1, 0]},
                "has_phone": {"$cond": [{"$ne": ["$phone", None]}, 1, 0]},
                "has_dob": {"$cond": [{"$ne": ["$dateOfBirth", None]}, 1, 0]}
            }},
            {"$group": {
                "_id": None,
                "total_with_email": {"$sum": "$has_email"},
                "total_with_phone": {"$sum": "$has_phone"},
                "total_with_dob": {"$sum": "$has_dob"},
                "total_students": {"$sum": 1}
            }}
        ])
        
        demographic_analysis = {
            "year_distribution": {demo["_id"]: demo["count"] for demo in year_demographics if demo["_id"]},
            "batch_distribution": {demo["_id"]: demo["count"] for demo in batch_demographics if demo["_id"]},
            "age_distribution": {demo["_id"]: demo["count"] for demo in age_demographics},
            "contact_completeness": {
                "total_students": contact_completeness[0].get("total_students", 0) if contact_completeness else 0,
                "with_email": contact_completeness[0].get("total_with_email", 0) if contact_completeness else 0,
                "with_phone": contact_completeness[0].get("total_with_phone", 0) if contact_completeness else 0,
                "with_dob": contact_completeness[0].get("total_with_dob", 0) if contact_completeness else 0,
                "email_percentage": round((contact_completeness[0].get("total_with_email", 0) / contact_completeness[0].get("total_students", 1) * 100), 2) if contact_completeness else 0,
                "phone_percentage": round((contact_completeness[0].get("total_with_phone", 0) / contact_completeness[0].get("total_students", 1) * 100), 2) if contact_completeness else 0,
                "dob_percentage": round((contact_completeness[0].get("total_with_dob", 0) / contact_completeness[0].get("total_students", 1) * 100), 2) if contact_completeness else 0
            }
        }
        
        return format_success_response(
            demographic_analysis,
            "Demographic analysis retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting demographic analysis: {e}")
        return format_error_response(e, "Failed to retrieve demographic analysis")


async def generate_academic_report() -> Dict[str, Any]:
    """
    Generate comprehensive academic report combining all analytics.
    """
    try:
        # Get all analytics data
        enrollment_stats = await get_enrollment_stats()
        leave_analytics = await get_leave_analytics()
        faculty_workload = await get_faculty_workload_report()
        course_popularity = await get_course_popularity()
        demographic_analysis = await get_demographic_analysis()
        
        # Combine all reports
        academic_report = {
            "report_generated_at": datetime.now().isoformat(),
            "enrollment_statistics": enrollment_stats.get("data", {}),
            "leave_analytics": leave_analytics.get("data", {}),
            "faculty_workload": faculty_workload.get("data", {}),
            "course_popularity": course_popularity.get("data", {}),
            "demographic_analysis": demographic_analysis.get("data", {}),
            "summary": {
                "total_students": enrollment_stats.get("data", {}).get("total_students", 0),
                "total_faculty": faculty_workload.get("data", {}).get("total_faculty", 0),
                "total_courses": course_popularity.get("data", {}).get("total_courses", 0),
                "total_leaves": leave_analytics.get("data", {}).get("total_leaves", 0),
                "faculty_assignment_rate": course_popularity.get("data", {}).get("faculty_assignment_rate", 0)
            }
        }
        
        return format_success_response(
            academic_report,
            "Comprehensive academic report generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating academic report: {e}")
        return format_error_response(e, "Failed to generate academic report")


# MCP Tool definitions
def get_analytics_tools() -> List[Tool]:
    """Get all analytics tools."""
    return [
        Tool(
            name="get_enrollment_stats",
            description="Get student enrollment statistics and analytics",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_attendance_summary",
            description="Get attendance summary statistics",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_leave_analytics",
            description="Get leave pattern analysis and statistics",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_faculty_workload_report",
            description="Get faculty workload distribution and teaching load analysis",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_course_popularity",
            description="Get course enrollment trends and popularity analysis",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_demographic_analysis",
            description="Get student demographic analysis",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="generate_academic_report",
            description="Generate comprehensive academic report combining all analytics",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]
