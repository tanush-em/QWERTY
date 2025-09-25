#!/usr/bin/env python3
"""
Sample data generation script for CSE-AIML ERP MCP Server.
This script creates sample data for testing and demonstration purposes.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from bson import ObjectId

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database import get_db_operations
from src.utils.validators import validate_student_data, validate_faculty_data, validate_course_data


async def create_sample_data():
    """Create sample data for all collections."""
    print("Creating sample data for CSE-AIML ERP...")
    
    try:
        # Get database operations
        db_ops = await get_db_operations()
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("Clearing existing data...")
        await db_ops.delete_one("students", {})  # This will only delete one document
        await db_ops.delete_one("faculties", {})
        await db_ops.delete_one("courses", {})
        await db_ops.delete_one("leaves", {})
        await db_ops.delete_one("timetables", {})
        
        # Create sample students
        print("Creating sample students...")
        students_data = [
            {
                "roll": "CSE001",
                "fullName": "Alice Johnson",
                "email": "alice.johnson@example.com",
                "phone": "+1234567890",
                "year": "2024",
                "batch": "A",
                "dateOfBirth": "2000-03-15",
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            },
            {
                "roll": "CSE002",
                "fullName": "Bob Smith",
                "email": "bob.smith@example.com",
                "phone": "+1234567891",
                "year": "2024",
                "batch": "A",
                "dateOfBirth": "2000-07-22",
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            },
            {
                "roll": "CSE003",
                "fullName": "Carol Williams",
                "email": "carol.williams@example.com",
                "phone": "+1234567892",
                "year": "2023",
                "batch": "B",
                "dateOfBirth": "1999-11-08",
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            },
            {
                "roll": "CSE004",
                "fullName": "David Brown",
                "email": "david.brown@example.com",
                "phone": "+1234567893",
                "year": "2023",
                "batch": "B",
                "dateOfBirth": "1999-05-30",
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            },
            {
                "roll": "CSE005",
                "fullName": "Eva Davis",
                "email": "eva.davis@example.com",
                "phone": "+1234567894",
                "year": "2025",
                "batch": "C",
                "dateOfBirth": "2001-01-12",
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            }
        ]
        
        student_ids = []
        for student_data in students_data:
            student_id = await db_ops.insert_one("students", student_data)
            student_ids.append(student_id)
            print(f"Created student: {student_data['roll']} - {student_data['fullName']}")
        
        # Create sample faculties
        print("Creating sample faculties...")
        faculties_data = [
            {
                "employeeId": "EMP001",
                "fullName": "Dr. John Professor",
                "email": "john.professor@example.com",
                "phone": "+1234567800",
                "designation": "Professor",
                "subjects": ["Data Structures", "Algorithms", "Computer Networks"],
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            },
            {
                "employeeId": "EMP002",
                "fullName": "Dr. Jane Assistant",
                "email": "jane.assistant@example.com",
                "phone": "+1234567801",
                "designation": "Assistant Professor",
                "subjects": ["Programming", "Database Systems"],
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            },
            {
                "employeeId": "EMP003",
                "fullName": "Dr. Mike Associate",
                "email": "mike.associate@example.com",
                "phone": "+1234567802",
                "designation": "Associate Professor",
                "subjects": ["Machine Learning", "Artificial Intelligence"],
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            },
            {
                "employeeId": "EMP004",
                "fullName": "Dr. Sarah Lecturer",
                "email": "sarah.lecturer@example.com",
                "phone": "+1234567803",
                "designation": "Lecturer",
                "subjects": ["Mathematics", "Statistics"],
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            }
        ]
        
        faculty_ids = []
        for faculty_data in faculties_data:
            faculty_id = await db_ops.insert_one("faculties", faculty_data)
            faculty_ids.append(faculty_id)
            print(f"Created faculty: {faculty_data['employeeId']} - {faculty_data['fullName']}")
        
        # Create sample courses
        print("Creating sample courses...")
        courses_data = [
            {
                "code": "CS101",
                "title": "Introduction to Programming",
                "credits": 3,
                "semester": 1,
                "facultyInCharge": faculty_ids[1],  # Dr. Jane Assistant
                "description": "Basic programming concepts and problem solving",
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            },
            {
                "code": "CS102",
                "title": "Data Structures",
                "credits": 4,
                "semester": 2,
                "facultyInCharge": faculty_ids[0],  # Dr. John Professor
                "description": "Fundamental data structures and algorithms",
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            },
            {
                "code": "CS201",
                "title": "Algorithms",
                "credits": 4,
                "semester": 3,
                "facultyInCharge": faculty_ids[0],  # Dr. John Professor
                "description": "Algorithm design and analysis",
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            },
            {
                "code": "CS202",
                "title": "Database Systems",
                "credits": 3,
                "semester": 4,
                "facultyInCharge": faculty_ids[1],  # Dr. Jane Assistant
                "description": "Database design and management",
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            },
            {
                "code": "CS301",
                "title": "Machine Learning",
                "credits": 4,
                "semester": 5,
                "facultyInCharge": faculty_ids[2],  # Dr. Mike Associate
                "description": "Introduction to machine learning algorithms",
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            },
            {
                "code": "CS302",
                "title": "Computer Networks",
                "credits": 3,
                "semester": 6,
                "facultyInCharge": faculty_ids[0],  # Dr. John Professor
                "description": "Network protocols and architectures",
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            }
        ]
        
        course_ids = []
        for course_data in courses_data:
            course_id = await db_ops.insert_one("courses", course_data)
            course_ids.append(course_id)
            print(f"Created course: {course_data['code']} - {course_data['title']}")
        
        # Create sample leaves
        print("Creating sample leave applications...")
        leaves_data = [
            {
                "studentId": student_ids[0],  # Alice Johnson
                "startDate": "2024-02-15",
                "endDate": "2024-02-16",
                "reason": "Medical emergency - family member",
                "status": "approved",
                "handledBy": faculty_ids[0],  # Dr. John Professor
                "remarks": "Approved due to medical emergency",
                "createdAt": datetime.now() - timedelta(days=5),
                "updatedAt": datetime.now() - timedelta(days=3)
            },
            {
                "studentId": student_ids[1],  # Bob Smith
                "startDate": "2024-02-20",
                "endDate": "2024-02-22",
                "reason": "Personal work - job interview",
                "status": "pending",
                "handledBy": None,
                "remarks": None,
                "createdAt": datetime.now() - timedelta(days=2),
                "updatedAt": datetime.now() - timedelta(days=2)
            },
            {
                "studentId": student_ids[2],  # Carol Williams
                "startDate": "2024-01-25",
                "endDate": "2024-01-26",
                "reason": "Family function",
                "status": "approved",
                "handledBy": faculty_ids[1],  # Dr. Jane Assistant
                "remarks": "Approved for family function",
                "createdAt": datetime.now() - timedelta(days=10),
                "updatedAt": datetime.now() - timedelta(days=8)
            },
            {
                "studentId": student_ids[3],  # David Brown
                "startDate": "2024-02-10",
                "endDate": "2024-02-12",
                "reason": "Sick leave",
                "status": "rejected",
                "handledBy": faculty_ids[2],  # Dr. Mike Associate
                "remarks": "Rejected - insufficient documentation",
                "createdAt": datetime.now() - timedelta(days=7),
                "updatedAt": datetime.now() - timedelta(days=5)
            }
        ]
        
        for leave_data in leaves_data:
            leave_id = await db_ops.insert_one("leaves", leave_data)
            print(f"Created leave application for student {leave_data['studentId']}")
        
        # Create sample timetable
        print("Creating sample timetable...")
        timetables_data = [
            {
                "dayOfWeek": "monday",
                "slots": [
                    {
                        "period": 1,
                        "startTime": "09:00",
                        "endTime": "10:00",
                        "type": "class",
                        "courseCode": "CS101",
                        "facultyId": faculty_ids[1],  # Dr. Jane Assistant
                        "room": "A101"
                    },
                    {
                        "period": 2,
                        "startTime": "10:00",
                        "endTime": "11:00",
                        "type": "class",
                        "courseCode": "CS102",
                        "facultyId": faculty_ids[0],  # Dr. John Professor
                        "room": "A102"
                    },
                    {
                        "period": 3,
                        "startTime": "11:15",
                        "endTime": "12:15",
                        "type": "break",
                        "courseCode": None,
                        "facultyId": None,
                        "room": None
                    },
                    {
                        "period": 4,
                        "startTime": "12:15",
                        "endTime": "13:15",
                        "type": "class",
                        "courseCode": "CS201",
                        "facultyId": faculty_ids[0],  # Dr. John Professor
                        "room": "A103"
                    }
                ],
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            },
            {
                "dayOfWeek": "tuesday",
                "slots": [
                    {
                        "period": 1,
                        "startTime": "09:00",
                        "endTime": "10:00",
                        "type": "class",
                        "courseCode": "CS202",
                        "facultyId": faculty_ids[1],  # Dr. Jane Assistant
                        "room": "A101"
                    },
                    {
                        "period": 2,
                        "startTime": "10:00",
                        "endTime": "11:00",
                        "type": "class",
                        "courseCode": "CS301",
                        "facultyId": faculty_ids[2],  # Dr. Mike Associate
                        "room": "A102"
                    },
                    {
                        "period": 3,
                        "startTime": "11:15",
                        "endTime": "12:15",
                        "type": "lunch",
                        "courseCode": None,
                        "facultyId": None,
                        "room": None
                    },
                    {
                        "period": 4,
                        "startTime": "12:15",
                        "endTime": "13:15",
                        "type": "class",
                        "courseCode": "CS302",
                        "facultyId": faculty_ids[0],  # Dr. John Professor
                        "room": "A103"
                    }
                ],
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            }
        ]
        
        for timetable_data in timetables_data:
            timetable_id = await db_ops.insert_one("timetables", timetable_data)
            print(f"Created timetable for {timetable_data['dayOfWeek']}")
        
        print("\nSample data creation completed successfully!")
        print(f"Created:")
        print(f"- {len(student_ids)} students")
        print(f"- {len(faculty_ids)} faculty members")
        print(f"- {len(course_ids)} courses")
        print(f"- {len(leaves_data)} leave applications")
        print(f"- {len(timetables_data)} timetable entries")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        raise


async def main():
    """Main function."""
    try:
        await create_sample_data()
    except Exception as e:
        print(f"Failed to create sample data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
