#!/usr/bin/env python3
"""
Sample data script for CSE-AIML ERP System
Run this script to populate the database with sample data
"""

from pymongo import MongoClient
from datetime import datetime, date
from bson import ObjectId

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['cse_aiml_erp']

# Collections
students = db['students']
faculties = db['faculties']
courses = db['courses']
leaves = db['leaves']
timetable = db['timetable']

def clear_collections():
    """Clear all collections"""
    students.delete_many({})
    faculties.delete_many({})
    courses.delete_many({})
    leaves.delete_many({})
    timetable.delete_many({})
    print("Cleared all collections")

def insert_sample_courses():
    """Insert sample courses"""
    course_data = [
        {
            "code": "191CAC701T",
            "title": "Deep Learning (PE-III)",
            "credits": 3,
            "semester": 7,
            "description": "Deep Learning concepts and applications"
        },
        {
            "code": "191AIE091T",
            "title": "Introduction To NOSQL Databases (PE-III)",
            "credits": 3,
            "semester": 7,
            "description": "Introduction to NoSQL database systems"
        },
        {
            "code": "191CAE084J",
            "title": "Ethics and AI (PE-IV)",
            "credits": 3,
            "semester": 8,
            "description": "Ethical considerations in Artificial Intelligence"
        },
        {
            "code": "191MEO704T",
            "title": "Supply Chain Management And Logistics (OE-III)",
            "credits": 3,
            "semester": 7,
            "description": "Supply chain management and logistics principles"
        },
        {
            "code": "191CAC711L",
            "title": "Deep Learning Laboratory",
            "credits": 2,
            "semester": 7,
            "description": "Practical implementation of Deep Learning algorithms"
        },
        {
            "code": "191CAP711J",
            "title": "Project Work / Startup - Phase - I",
            "credits": 4,
            "semester": 7,
            "description": "Project work and startup phase implementation"
        },
        {
            "code": "COUN",
            "title": "Counseling",
            "credits": 0,
            "semester": 7,
            "description": "Student counseling and guidance"
        },
        {
            "code": "PT",
            "title": "Placement Training",
            "credits": 0,
            "semester": 7,
            "description": "Placement preparation and training"
        }
    ]
    
    result = courses.insert_many(course_data)
    print(f"Inserted {len(result.inserted_ids)} courses")
    return result.inserted_ids

def insert_sample_faculties(course_ids):
    """Insert sample faculties"""
    faculty_data = [
        {
            "employeeId": "FAC-01",
            "fullName": "Dr.S.Vanaja",
            "email": "s.vanaja@college.edu",
            "designation": "Associate Professor",
            "subjects": [course_ids[0], course_ids[4], course_ids[5]]  # Deep Learning, Deep Learning Lab, Project Work
        },
        {
            "employeeId": "FAC-02",
            "fullName": "Dr.G.Jeyaram",
            "email": "g.jeyaram@college.edu",
            "designation": "Professor",
            "subjects": [course_ids[1], course_ids[6], course_ids[7]]  # NoSQL, Counseling, Placement Training
        },
        {
            "employeeId": "FAC-03",
            "fullName": "Mrs.D.Saranya",
            "email": "d.saranya@college.edu",
            "designation": "Assistant Professor",
            "subjects": [course_ids[2], course_ids[4]]  # Ethics and AI, Deep Learning Lab
        },
        {
            "employeeId": "FAC-04",
            "fullName": "Dr.D.Sakthimurugan",
            "email": "d.sakthimurugan@college.edu",
            "designation": "Associate Professor",
            "subjects": [course_ids[3]]  # Supply Chain Management
        }
    ]
    
    result = faculties.insert_many(faculty_data)
    print(f"Inserted {len(result.inserted_ids)} faculties")
    return result.inserted_ids

def insert_sample_students():
    """Insert sample students"""
    student_data = [
        {
            "roll": 1,
            "fullName": "Aisha Khan",
            "email": "aisha@college.edu",
            "phone": "+91-9876543210",
            "year": 4,
            "batch": 2024,
            "dateOfBirth": datetime(2003, 5, 12),
            "addresses": [
                {
                    "type": "permanent",
                    "line1": "123 Main Street",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "pincode": "400001"
                }
            ]
        },
        {
            "roll": 2,
            "fullName": "Rajesh Kumar",
            "email": "rajesh@college.edu",
            "phone": "+91-9876543211",
            "year": 4,
            "batch": 2024,
            "dateOfBirth": datetime(2003, 8, 15),
            "addresses": [
                {
                    "type": "permanent",
                    "line1": "456 Park Avenue",
                    "city": "Delhi",
                    "state": "Delhi",
                    "pincode": "110001"
                }
            ]
        },
        {
            "roll": 3,
            "fullName": "Priya Sharma",
            "email": "priya@college.edu",
            "phone": "+91-9876543212",
            "year": 4,
            "batch": 2024,
            "dateOfBirth": datetime(2003, 3, 22),
            "addresses": [
                {
                    "type": "permanent",
                    "line1": "789 Garden Road",
                    "city": "Bangalore",
                    "state": "Karnataka",
                    "pincode": "560001"
                }
            ]
        },
        {
            "roll": 4,
            "fullName": "Amit Singh",
            "email": "amit@college.edu",
            "phone": "+91-9876543213",
            "year": 4,
            "batch": 2024,
            "dateOfBirth": datetime(2003, 11, 8),
            "addresses": [
                {
                    "type": "permanent",
                    "line1": "321 Lake View",
                    "city": "Chennai",
                    "state": "Tamil Nadu",
                    "pincode": "600001"
                }
            ]
        },
        {
            "roll": 5,
            "fullName": "Sneha Reddy",
            "email": "sneha@college.edu",
            "phone": "+91-9876543214",
            "year": 4,
            "batch": 2024,
            "dateOfBirth": datetime(2003, 7, 30),
            "addresses": [
                {
                    "type": "permanent",
                    "line1": "654 Hill Station",
                    "city": "Hyderabad",
                    "state": "Telangana",
                    "pincode": "500001"
                }
            ]
        }
    ]
    
    result = students.insert_many(student_data)
    print(f"Inserted {len(result.inserted_ids)} students")
    return result.inserted_ids

def insert_sample_leaves(student_ids):
    """Insert sample leave applications"""
    leave_data = [
        {
            "studentId": student_ids[0],  # Aisha Khan
            "startDate": datetime(2024, 8, 15),
            "endDate": datetime(2024, 8, 17),
            "reason": "Medical - fever",
            "handledBy": None
        },
        {
            "studentId": student_ids[1],  # Rajesh Kumar
            "startDate": datetime(2024, 8, 20),
            "endDate": datetime(2024, 8, 22),
            "reason": "Family emergency",
            "handledBy": None
        },
        {
            "studentId": student_ids[2],  # Priya Sharma
            "startDate": datetime(2024, 8, 25),
            "endDate": datetime(2024, 8, 27),
            "reason": "Personal work",
            "handledBy": None
        }
    ]
    
    result = leaves.insert_many(leave_data)
    print(f"Inserted {len(result.inserted_ids)} leave applications")

def insert_timetable_data():
    """Insert timetable data"""
    timetable_data = [
        {
            "dayOfWeek": "Monday",
            "slots": [
                { "period": 1, "startTime": "09:00", "endTime": "10:00", "type": "lecture", "courseCode": "DL",    "room": "R101" },
                { "period": 2, "startTime": "10:00", "endTime": "11:00", "type": "lecture", "courseCode": "NOSQL", "room": "R102" },
                { "period": 3, "startTime": "11:15", "endTime": "12:15", "type": "lecture", "courseCode": "SCM",   "room": "R103" },
                { "period": 4, "startTime": "12:15", "endTime": "13:15", "type": "lecture", "courseCode": "DL",    "room": "R101" },
                { "period": 5, "startTime": "13:15", "endTime": "13:45", "type": "break",   "courseCode": None },
                { "period": 6, "startTime": "13:45", "endTime": "14:45", "type": "lecture", "courseCode": "EAI",   "room": "R104" },
                { "period": 7, "startTime": "14:45", "endTime": "15:45", "type": "lecture", "courseCode": "NOSQL", "room": "R102" },
                { "period": 8, "startTime": "15:45", "endTime": "16:45", "type": "lecture", "courseCode": "COU",   "room": "R105" }
            ]
        },
        {
            "dayOfWeek": "Tuesday",
            "slots": [
                { "period": 1, "startTime": "09:00", "endTime": "10:00", "type": "lecture", "courseCode": "DLL/PW", "room": "Lab 1" },
                { "period": 2, "startTime": "10:00", "endTime": "11:00", "type": "lecture", "courseCode": "DLL/PW", "room": "Lab 1" },
                { "period": 3, "startTime": "11:15", "endTime": "12:15", "type": "lecture", "courseCode": "SCM",    "room": "R103" },
                { "period": 4, "startTime": "12:15", "endTime": "13:15", "type": "lecture", "courseCode": "EAI",    "room": "R104" },
                { "period": 5, "startTime": "13:15", "endTime": "13:45", "type": "break" },
                { "period": 6, "startTime": "13:45", "endTime": "14:45", "type": "lecture", "courseCode": "DL",     "room": "R101" },
                { "period": 7, "startTime": "14:45", "endTime": "15:45", "type": "lecture", "courseCode": "NOSQL",  "room": "R102" }
            ]
        },
        {
            "dayOfWeek": "Wednesday",
            "slots": [
                { "period": 1, "startTime": "09:00", "endTime": "10:00", "type": "lecture", "courseCode": "NOSQL", "room": "R102" },
                { "period": 2, "startTime": "10:00", "endTime": "11:00", "type": "lecture", "courseCode": "DL",    "room": "R101" },
                { "period": 3, "startTime": "11:15", "endTime": "12:15", "type": "lecture", "courseCode": "SCM",   "room": "R103" },
                { "period": 4, "startTime": "12:15", "endTime": "13:15", "type": "lecture", "courseCode": "NOSQL", "room": "R102" },
                { "period": 5, "startTime": "13:15", "endTime": "13:45", "type": "break" },
                { "period": 6, "startTime": "13:45", "endTime": "14:45", "type": "lecture", "courseCode": "EAI",   "room": "R104" },
                { "period": 7, "startTime": "14:45", "endTime": "15:45", "type": "lecture", "courseCode": "SCM",   "room": "R103" }
            ]
        },
        {
            "dayOfWeek": "Thursday",
            "slots": [
                { "period": 1, "startTime": "09:00", "endTime": "10:00", "type": "lecture", "courseCode": "EAI",    "room": "R104" },
                { "period": 2, "startTime": "10:00", "endTime": "11:00", "type": "lecture", "courseCode": "SCM",    "room": "R103" },
                { "period": 3, "startTime": "11:15", "endTime": "12:15", "type": "lecture", "courseCode": "DL",     "room": "R101" },
                { "period": 4, "startTime": "12:15", "endTime": "13:15", "type": "lecture", "courseCode": "SCM",    "room": "R103" },
                { "period": 5, "startTime": "13:15", "endTime": "13:45", "type": "break" },
                { "period": 6, "startTime": "13:45", "endTime": "14:45", "type": "lecture", "courseCode": "DLL/PW", "room": "Lab 2" },
                { "period": 7, "startTime": "14:45", "endTime": "15:45", "type": "lecture", "courseCode": "DL",     "room": "R101" }
            ]
        },
        {
            "dayOfWeek": "Friday",
            "slots": [
                { "period": 1, "startTime": "09:00", "endTime": "10:00", "type": "lecture", "courseCode": "SCM",    "room": "R103" },
                { "period": 2, "startTime": "10:00", "endTime": "11:00", "type": "lecture", "courseCode": "NOSQL",  "room": "R102" },
                { "period": 3, "startTime": "11:15", "endTime": "12:15", "type": "lecture", "courseCode": "DL",     "room": "R101" },
                { "period": 4, "startTime": "12:15", "endTime": "13:15", "type": "lecture", "courseCode": "NOSQL",  "room": "R102" },
                { "period": 5, "startTime": "13:15", "endTime": "13:45", "type": "break" },
                { "period": 6, "startTime": "13:45", "endTime": "14:45", "type": "lecture", "courseCode": "EAI",    "room": "R104" },
                { "period": 7, "startTime": "14:45", "endTime": "16:45", "type": "lab",     "courseCode": "PT",     "room": "Lab 3" }
            ]
        }
    ]
    
    result = timetable.insert_many(timetable_data)
    print(f"Inserted {len(result.inserted_ids)} timetable days")
    return result.inserted_ids

def link_courses_with_faculty(course_ids, faculty_ids):
    """Link courses with their respective faculty members"""
    # Course to faculty mapping based on the table data
    course_faculty_mapping = {
        0: 0,  # Deep Learning -> Dr.S.Vanaja
        1: 1,  # NoSQL -> Dr.G.Jeyaram  
        2: 2,  # Ethics and AI -> Mrs.D.Saranya
        3: 3,  # Supply Chain -> Dr.D.Sakthimurugan
        4: 0,  # Deep Learning Lab -> Dr.S.Vanaja
        5: 0,  # Project Work -> Dr.S.Vanaja
        6: 1,  # Counseling -> Dr.G.Jeyaram
        7: 1,  # Placement Training -> Dr.G.Jeyaram
    }
    
    # Update courses with facultyInCharge
    for i, course_id in enumerate(course_ids):
        if i in course_faculty_mapping:
            faculty_index = course_faculty_mapping[i]
            faculty_id = faculty_ids[faculty_index]
            courses.update_one(
                {"_id": course_id},
                {"$set": {"facultyInCharge": faculty_id}}
            )
    
    print("Linked courses with faculty members")

def main():
    """Main function to populate sample data"""
    print("Starting to populate sample data...")
    
    # Clear existing data
    clear_collections()
    
    # Insert data in order (courses first, then faculties, then students, then leaves, then timetable)
    course_ids = insert_sample_courses()
    faculty_ids = insert_sample_faculties(course_ids)
    student_ids = insert_sample_students()
    insert_sample_leaves(student_ids)
    insert_timetable_data()
    
    # Link courses with faculty members
    link_courses_with_faculty(course_ids, faculty_ids)
    
    print("Sample data population completed!")
    print(f"Database: {db.name}")
    print("Collections populated:")
    print(f"- Students: {students.count_documents({})}")
    print(f"- Faculties: {faculties.count_documents({})}")
    print(f"- Courses: {courses.count_documents({})}")
    print(f"- Leaves: {leaves.count_documents({})}")
    print(f"- Timetable Days: {timetable.count_documents({})}")

if __name__ == "__main__":
    main()
